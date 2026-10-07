import re

from markdown_it import MarkdownIt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from .layout import Cursor, MARGIN, CONTENT_W, PAGE_W, BOTTOM_Y, TOP_Y

FIELD_RE = re.compile(r"\{\{([\w.]+)\}\}")
FIELD_WIDTH = {"text": 140, "checkbox": 12, "choice": 120, "radio": 120}
FIELD_HEIGHT = {"text": 14, "checkbox": 12, "choice": 14, "radio": 14}

FONT = "Helvetica"
SIZE = 9
LEADING = 12


def extract_text(inline_token):
    parts = []
    for child in inline_token.children or []:
        if child.type == "text":
            parts.append(child.content)
        elif child.type in ("softbreak", "hardbreak"):
            parts.append(" ")
        elif child.type == "code_inline":
            parts.append(child.content)
    return "".join(parts)


def build_blocks(tokens):
    """Regroupe le flux de tokens markdown-it en blocs (titre, paragraphe, liste, tableau)."""
    blocks = []
    i = 0
    section = None
    current_row = None
    header, rows = None, None
    while i < len(tokens):
        t = tokens[i]
        if t.type == "heading_open":
            blocks.append({"type": "heading", "level": int(t.tag[1]), "text": extract_text(tokens[i + 1])})
        elif t.type == "paragraph_open" and header is None:
            blocks.append({"type": "paragraph", "text": extract_text(tokens[i + 1])})
        elif t.type == "bullet_list_open":
            items = []
            i += 1
            while tokens[i].type != "bullet_list_close":
                if tokens[i].type == "inline":
                    items.append(extract_text(tokens[i]))
                i += 1
            blocks.append({"type": "list", "items": items})
        elif t.type == "table_open":
            header, rows = [], []
        elif t.type == "thead_open":
            section = "head"
        elif t.type == "tbody_open":
            section = "body"
        elif t.type == "tr_open":
            current_row = []
        elif t.type in ("th_open", "td_open"):
            current_row.append(extract_text(tokens[i + 1]))
        elif t.type == "tr_close":
            (header.extend(current_row) if section == "head" else rows.append(current_row))
            current_row = None
        elif t.type == "table_close":
            blocks.append({"type": "table", "header": header, "rows": rows})
            header, rows, section = None, None, None
        i += 1
    return blocks


FIELD_LINE_RE = re.compile(r"^(.+?)\s*:\s*\{\{([\w.]+)\}\}$")
WIDE_FIELD_RE = re.compile(r"^\{\{([\w.]+)\}\}$")


def group_field_lists(blocks):
    """Regroupe les paragraphes consécutifs de la forme « Libellé : {{field_id}} » en un
    bloc field_list, pour que tous les champs de saisie partagent la même abscisse plutôt
    que d'être posés juste après un libellé de longueur variable (cf. draw_field_list).
    Un paragraphe qui ne contient QU'un champ (rien d'autre, pas même un libellé) devient
    un bloc wide_field : la zone de saisie prend alors toute la largeur de la page plutôt
    que la largeur par défaut du type de champ (cf. draw_wide_field)."""
    out = []
    i = 0
    while i < len(blocks):
        b = blocks[i]
        wm = WIDE_FIELD_RE.match(b["text"]) if b["type"] == "paragraph" else None
        if wm:
            out.append({"type": "wide_field", "field_id": wm.group(1)})
            i += 1
            continue
        m = FIELD_LINE_RE.match(b["text"]) if b["type"] == "paragraph" else None
        if m:
            items = [(m.group(1), m.group(2))]
            i += 1
            while i < len(blocks) and blocks[i]["type"] == "paragraph":
                m2 = FIELD_LINE_RE.match(blocks[i]["text"])
                if not m2:
                    break
                items.append((m2.group(1), m2.group(2)))
                i += 1
            out.append({"type": "field_list", "items": items})
        else:
            out.append(b)
            i += 1
    return out


def tokenize_run(text):
    """Découpe un texte en une liste ordonnée de ('text', mot) et ('field', field_id)."""
    out = []
    pos = 0
    for m in FIELD_RE.finditer(text):
        out += [("text", w) for w in text[pos:m.start()].split()]
        out.append(("field", m.group(1)))
        pos = m.end()
    out += [("text", w) for w in text[pos:].split()]
    return out


# Pour un champ "radio" : un même `id` de champ est posé à plusieurs endroits du corps
# (une fois par ligne d'un tableau, par ex.) ; chaque occurrence forme un bouton radio
# distinct du MÊME groupe PDF (un seul nommé, plusieurs widgets), la valeur "on" de
# chaque widget étant son numéro d'occurrence (1, 2, 3…). Compteur remis à zéro par
# `generate()` à chaque génération de PDF.
_radio_occurrences = {}


def draw_field(c, f, x, y, width=None):
    w = width or FIELD_WIDTH.get(f.type, 100)
    h = FIELD_HEIGHT.get(f.type, 14)
    if f.type == "text":
        kwargs = {"value": f.default} if f.default else {}
        c.acroForm.textfield(name=f.id, x=x, y=y - 2, width=w, height=h, maxlen=f.maxlen,
                              fontSize=SIZE - 1, borderStyle="underlined", forceBorder=True,
                              **kwargs)
    elif f.type == "checkbox":
        c.acroForm.checkbox(name=f.id, x=x, y=y - 2, size=h, buttonStyle="check", borderStyle="solid")
    elif f.type == "radio":
        idx = _radio_occurrences.get(f.id, 0) + 1
        _radio_occurrences[f.id] = idx
        c.acroForm.radio(name=f.id, value=str(idx), selected=False, x=x, y=y - 2, size=h,
                          buttonStyle="circle", borderStyle="solid")
    else:  # choice -> rendu comme une liste déroulante (une seule valeur sélectionnée)
        # "-" ajouté uniquement à l'affichage PDF (pas dans f.options / le schéma JSON) :
        # sans ça, la liste préremplit silencieusement sa première vraie valeur, ce qui
        # a) rend mal tant que le client n'a pas interagi avec le widget, et
        # b) peut passer inaperçu si le client ne corrige pas une valeur plausible mais fausse.
        options = ["-"] + (f.options or [])
        c.acroForm.choice(name=f.id, x=x, y=y - 2, width=w, height=h, options=options, value=options[0])
    return w


def draw_run(c, cursor, text, fields_by_id, x0, max_width, font=FONT, size=SIZE):
    words = tokenize_run(text)
    x = x0
    space_w = c.stringWidth(" ", font, size)
    cursor.ensure_space(LEADING)
    cursor.y -= size * 0.8  # réserve l'ascendant de la première ligne
    for kind, value in words:
        if kind == "field":
            f = fields_by_id[value]
            w = FIELD_WIDTH.get(f.type, 100)
            if x > x0 and x + w > x0 + max_width:
                cursor.y -= LEADING
                cursor.ensure_space(LEADING)
                x = x0
            draw_field(c, f, x, cursor.y)
            x += w + 4
        else:
            w = c.stringWidth(value, font, size)
            if x > x0 and x + w > x0 + max_width:
                cursor.y -= LEADING
                cursor.ensure_space(LEADING)
                x = x0
            c.setFont(font, size)
            c.drawString(x, cursor.y, value)
            x += w + space_w
    cursor.advance(size * 0.2, gap=4)


def draw_cell_inline(c, cell_text, fields_by_id, x, y, max_width):
    """Variante sans retour à la ligne, pour une cellule de tableau sur une seule ligne."""
    x0 = x
    space_w = c.stringWidth(" ", FONT, SIZE)
    for kind, value in tokenize_run(cell_text):
        if kind == "field":
            f = fields_by_id[value]
            w = min(FIELD_WIDTH.get(f.type, 100), max_width - (x - x0))
            draw_field(c, f, x, y, width=max(w, 20))
            x += w + 4
        else:
            c.setFont(FONT, SIZE)
            c.drawString(x, y, value)
            x += c.stringWidth(value, FONT, SIZE) + space_w


def draw_heading(c, cursor, text, level):
    size = {1: 15, 2: 12, 3: 10}.get(level, 10)
    font = "Helvetica-Bold"
    while c.stringWidth(text, font, size) > CONTENT_W and size > 8:
        size -= 1
    # Niveau 2 = les titres de section "A.", "B." … : une ligne vide supplémentaire avant,
    # sauf en tout début de page (sinon on gaspille de l'espace juste après un saut de page).
    extra_gap = LEADING if level == 2 else 0
    cursor.ensure_space(size + 10 + extra_gap)
    if extra_gap and cursor.y != TOP_Y:
        cursor.y -= extra_gap
    cursor.y -= size * 0.85  # réserve l'ascendant : évite le chevauchement avec le bloc précédent
    c.setFont(font, size)
    c.drawString(MARGIN, cursor.y, text)
    cursor.advance(size * 0.3, gap=8)


def draw_list(c, cursor, items, fields_by_id):
    for item in items:
        cursor.ensure_space(LEADING)
        c.setFont(FONT, SIZE)
        c.drawString(MARGIN, cursor.y - SIZE * 0.8, "•")  # aligné sur la ligne de base que draw_run va utiliser
        draw_run(c, cursor, item, fields_by_id, MARGIN + 12, CONTENT_W - 12)


COL_PADDING = 10
COL_MIN_W = 26


def fit_font_size(c, text, font, size, max_width, min_size=7):
    """Réduit la taille de police jusqu'à ce que `text` tienne dans `max_width` : même
    technique que draw_heading. Nécessaire en secours de compute_col_widths — quand la
    largeur totale "naturelle" des colonnes dépasse déjà CONTENT_W, la mise à l'échelle
    proportionnelle réduit les colonnes sans réduire le texte, qui peut alors déborder
    sur la colonne voisine (cf. les deux longs intitulés de la table D)."""
    while size > min_size and c.stringWidth(text, font, size) > max_width:
        size -= 1
    return size


NARROW_SUFFIX = " {s}"  # intitulé d'en-tête se terminant ainsi -> colonne volontairement étroite


def strip_narrow(header):
    """Sépare le texte d'en-tête affiché du marqueur ' {s}' (largeur réduite voulue)."""
    clean, narrow = [], []
    for h in header:
        if h.endswith(NARROW_SUFFIX):
            clean.append(h[: -len(NARROW_SUFFIX)])
            narrow.append(True)
        else:
            clean.append(h)
            narrow.append(False)
    return clean, narrow


def compute_col_widths(c, header, rows):
    """Largeur de colonne proportionnelle au texte réellement affiché, plutôt qu'un
    partage uniforme : une cellule texte libre (ex. libellé de rôle) peut être bien
    plus large qu'un intitulé d'en-tête, et déborderait sinon sur la colonne voisine,
    recouverte ensuite par son widget de champ (cf. "Responsable Examens"). Un en-tête
    marqué '{s}' (cf. NARROW_SUFFIX) force une colonne étroite, pour les champs dont la
    saisie est intrinsèquement courte (ex. code postal) malgré un intitulé plus long."""
    clean_header, narrow = strip_narrow(header)
    natural = [c.stringWidth(h, "Helvetica-Bold", SIZE) for h in clean_header]
    for i, is_narrow in enumerate(narrow):
        if is_narrow:
            natural[i] *= 0.45
    for row in rows:
        for i, cell in enumerate(row):
            if "{{" in cell or narrow[i]:
                continue  # largeur d'un champ gérée à part (FIELD_WIDTH, clampée à la colonne)
            natural[i] = max(natural[i], c.stringWidth(cell, FONT, SIZE))
    widths = [max(n + COL_PADDING, COL_MIN_W) for n in natural]
    total = sum(widths)
    scale = CONTENT_W / total
    return [w * scale for w in widths]


ROW_V_PAD = 4   # marge verticale (haut et bas) entre le cadre de ligne et son contenu
ROW_GAP = 2     # espace blanc entre deux lignes (évite que les cadres se chevauchent)
ROW_FIELD_H = max(FIELD_HEIGHT.values())  # 14 : le plus grand widget posé dans une cellule


def draw_table(c, cursor, header, rows, fields_by_id):
    col_widths = compute_col_widths(c, header, rows)
    header, _ = strip_narrow(header)  # le marqueur '{s}' ne doit pas s'afficher
    col_x = [MARGIN]
    for w in col_widths[:-1]:
        col_x.append(col_x[-1] + w)
    # Le cadre de chaque ligne est dimensionné pour contenir le plus grand widget
    # (hauteur fixe, posé via draw_field) avec une marge de part et d'autre ; texte et
    # champ partagent la même ligne de base, calculée depuis le bas du cadre.
    row_h = ROW_FIELD_H + 2 * ROW_V_PAD

    def draw_row(cells, bold=False):
        cursor.ensure_space(row_h)
        rect_top = cursor.y
        rect_bottom = cursor.y - row_h
        baseline = rect_bottom + ROW_V_PAD + 2  # draw_field positionne le widget à y-2
        for i, cell in enumerate(cells):
            x, w = col_x[i], col_widths[i]
            c.rect(x, rect_bottom, w, row_h)
            if bold:
                fs = fit_font_size(c, cell, "Helvetica-Bold", SIZE, w - 6)
                c.setFont("Helvetica-Bold", fs)
                c.drawString(x + 3, baseline, cell)
            else:
                draw_cell_inline(c, cell, fields_by_id, x + 3, baseline, w - 6)
        cursor.y = rect_bottom - ROW_GAP

    draw_row(header, bold=True)
    for r in rows:
        draw_row(r)


FIELD_LIST_MIN_W = 60


def draw_field_list(c, cursor, items, fields_by_id):
    """Suite de lignes « Libellé : champ » où tous les champs démarrent à la même
    abscisse (plutôt qu'immédiatement après un libellé de longueur variable)."""
    label_w = max(c.stringWidth(f"{label} : ", FONT, SIZE) for label, _ in items)
    field_x = MARGIN + label_w
    # Si le libellé le plus long du groupe est très large, l'abscisse commune peut
    # pousser le champ hors de la marge droite : on borne sa largeur à l'espace restant
    # (comme draw_cell_inline le fait déjà pour les tableaux).
    max_width = max(MARGIN + CONTENT_W - field_x, FIELD_LIST_MIN_W)
    row_h = ROW_FIELD_H + 2 * ROW_V_PAD

    for label, field_id in items:
        cursor.ensure_space(row_h)
        rect_bottom = cursor.y - row_h
        baseline = rect_bottom + ROW_V_PAD + 2
        c.setFont(FONT, SIZE)
        c.drawString(MARGIN, baseline, f"{label} :")
        f = fields_by_id[field_id]
        w = min(FIELD_WIDTH.get(f.type, 100), max_width)
        draw_field(c, f, field_x, baseline, width=w)
        cursor.y = rect_bottom - ROW_GAP


def draw_wide_field(c, cursor, field_id, fields_by_id):
    """Paragraphe ne contenant qu'un seul champ : la zone de saisie occupe toute la
    largeur de la page plutôt que la largeur par défaut de son type. Si le champ déclare
    `lines` > 1, le widget devient une vraie zone de texte multiligne, agrandie d'autant."""
    f = fields_by_id[field_id]
    lines = max(1, f.lines or 1)
    if f.type == "text" and lines > 1:
        height = lines * (ROW_FIELD_H - 2) + 6
        row_h = height + 2 * ROW_V_PAD
        cursor.ensure_space(row_h)
        rect_bottom = cursor.y - row_h
        c.acroForm.textfield(name=f.id, x=MARGIN, y=rect_bottom + ROW_V_PAD, width=CONTENT_W,
                              height=height, maxlen=f.maxlen, fontSize=SIZE - 1,
                              borderStyle="underlined", forceBorder=True, fieldFlags="multiline")
        cursor.y = rect_bottom - ROW_GAP
    else:
        row_h = ROW_FIELD_H + 2 * ROW_V_PAD
        cursor.ensure_space(row_h)
        rect_bottom = cursor.y - row_h
        baseline = rect_bottom + ROW_V_PAD + 2
        draw_field(c, f, MARGIN, baseline, width=CONTENT_W)
        cursor.y = rect_bottom - ROW_GAP


def generate(front, body, fields_by_id, out_path):
    _radio_occurrences.clear()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out_path), pagesize=A4)
    c.setTitle(front["form"]["title"])
    c.setAuthor("Certi-Trust FRANCE SAS")

    footer = front.get("pdf", {}).get("footer_label", "").format(
        document_version=front["form"]["document_version"],
        schema_version=front["form"]["schema_version"],
    )

    def on_new_page(canv, page_num):
        canv.setFont("Helvetica", 8)
        canv.drawCentredString(PAGE_W / 2, BOTTOM_Y - 14, f"{footer} — page {page_num}")

    cursor = Cursor(c, on_new_page=on_new_page)

    md = MarkdownIt("commonmark").enable("table")
    for block in group_field_lists(build_blocks(md.parse(body))):
        if block["type"] == "heading":
            draw_heading(c, cursor, block["text"], block["level"])
        elif block["type"] == "paragraph":
            draw_run(c, cursor, block["text"], fields_by_id, MARGIN, CONTENT_W)
        elif block["type"] == "list":
            draw_list(c, cursor, block["items"], fields_by_id)
        elif block["type"] == "table":
            draw_table(c, cursor, block["header"], block["rows"], fields_by_id)
        elif block["type"] == "field_list":
            draw_field_list(c, cursor, block["items"], fields_by_id)
        elif block["type"] == "wide_field":
            draw_wide_field(c, cursor, block["field_id"], fields_by_id)

    # champs cachés de traçabilité de version, lus plus tard par le widget (décision 3 - rétrocompatibilité)
    c.acroForm.textfield(name="_form_id", value=front["form"]["id"], x=2, y=2, width=1, height=1,
                          fieldFlags="readOnly")
    c.acroForm.textfield(name="_form_version", value=str(front["form"]["schema_version"]), x=2, y=2,
                          width=1, height=1, fieldFlags="readOnly")

    on_new_page(c, cursor.page_num)
    c.showPage()
    c.save()
