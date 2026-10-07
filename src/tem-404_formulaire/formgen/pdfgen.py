import re

from markdown_it import MarkdownIt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from .layout import Cursor, MARGIN, CONTENT_W, PAGE_W, BOTTOM_Y

FIELD_RE = re.compile(r"\{\{([\w.]+)\}\}")
FIELD_WIDTH = {"text": 140, "checkbox": 12, "choice": 120, "radio": 120}
FIELD_HEIGHT = {"text": 14, "checkbox": 12, "choice": 14, "radio": 14}

FONT = "Helvetica"
SIZE = 10
LEADING = 13


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


def draw_field(c, f, x, y, width=None):
    w = width or FIELD_WIDTH.get(f.type, 100)
    h = FIELD_HEIGHT.get(f.type, 14)
    if f.type == "text":
        c.acroForm.textfield(name=f.id, x=x, y=y - 2, width=w, height=h, maxlen=f.maxlen,
                              fontSize=9, borderStyle="underlined", forceBorder=True)
    elif f.type == "checkbox":
        c.acroForm.checkbox(name=f.id, x=x, y=y - 2, size=h, buttonStyle="check", borderStyle="solid")
    else:  # radio / choice -> rendu comme une liste déroulante (une seule valeur sélectionnée)
        options = f.options or [""]
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
    size = {1: 16, 2: 13, 3: 11}.get(level, 11)
    font = "Helvetica-Bold"
    while c.stringWidth(text, font, size) > CONTENT_W and size > 8:
        size -= 1
    cursor.ensure_space(size + 10)
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


def draw_table(c, cursor, header, rows, fields_by_id):
    ncols = len(header)
    col_w = CONTENT_W / ncols
    row_h = LEADING + 8

    def draw_row(cells, bold=False):
        cursor.ensure_space(row_h)
        top = cursor.y + 6
        for i, cell in enumerate(cells):
            x = MARGIN + i * col_w
            c.rect(x, top - row_h, col_w, row_h)
            if bold:
                c.setFont("Helvetica-Bold", SIZE)
                c.drawString(x + 3, cursor.y, cell)
            else:
                draw_cell_inline(c, cell, fields_by_id, x + 3, cursor.y, col_w - 6)
        cursor.y = top - row_h - 2

    draw_row(header, bold=True)
    for r in rows:
        draw_row(r)


def generate(front, body, fields_by_id, out_path):
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
    for block in build_blocks(md.parse(body)):
        if block["type"] == "heading":
            draw_heading(c, cursor, block["text"], block["level"])
        elif block["type"] == "paragraph":
            draw_run(c, cursor, block["text"], fields_by_id, MARGIN, CONTENT_W)
        elif block["type"] == "list":
            draw_list(c, cursor, block["items"], fields_by_id)
        elif block["type"] == "table":
            draw_table(c, cursor, block["header"], block["rows"], fields_by_id)

    # champs cachés de traçabilité de version, lus plus tard par le widget (décision 3 - rétrocompatibilité)
    c.acroForm.textfield(name="_form_id", value=front["form"]["id"], x=2, y=2, width=1, height=1,
                          fieldFlags="readOnly")
    c.acroForm.textfield(name="_form_version", value=str(front["form"]["schema_version"]), x=2, y=2,
                          width=1, height=1, fieldFlags="readOnly")

    on_new_page(c, cursor.page_num)
    c.showPage()
    c.save()
