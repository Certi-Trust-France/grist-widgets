---
objet: architecture du processus de génération du formulaire TEM-404 depuis un fichier md
maj: 2026-10-05
modèle de formulaire: src\tem-404_formulaire\TEM-404_Formulaire_application_cadrage_V7_0.pdf
---

# enjeux
L'objectif est décrit dans docs\specs\TEM-404_specs.md : déposer dans GRIST un formulaire pdf rempli par le client et remplir les tables.
Il faut pour cela pouvoir mettre à jour le widget et le formulaire.
Pour faciciliter cette tâche le formulaire est généré à partir d'un md : docs\specs\TEM-404_specs.md ## 5. Spécifications pour la génération du formulaire

# stack

- Python 3 (pas de venv dédié dans ce dépôt, interpréteur global)
- `reportlab` — génération du PDF et des champs AcroForm
- `markdown-it-py` (règle `table` activée) — parsing du corps markdown
- `pyyaml` — parsing du front matter
- Dépendances pinnées dans `src/tem-404_formulaire/requirements.txt`

# format du front matter du tem-404 au format md

## perplexity propose :

`---
form:
  id: demande_client
  title: Formulaire de demande client
  schema_version: 1.2.0
  document_version: 2026.10
  status: draft
  language: fr-FR

pdf:
  format: A4
  orientation: portrait
  output: dist/demande-client.pdf
  show_version: true
  version_label: "Version 2026.10"
  flatten: false

compatibility:
  minimum_widget_version: 1.0.0
  supported_schema_versions:
    - "1.x"

grist:
  table: Demandes
  widget_contract: demande_client
  mapping_mode: explicit

fields:
  - id: metadata.form_id
    pdf_name: metadata.form_id
    grist_column: Form_Id
    type: text
    source: generated
    default: demande_client
    required: true

  - id: metadata.schema_version
    pdf_name: metadata.schema_version
    grist_column: Form_SchemaVersion
    type: text
    source: generated
    default: 1.2.0
    required: true
`---

Les propriétés importantes sont :
    form.id : identité fonctionnelle du formulaire.
    schema_version : version du contrat de données.
    document_version : version publiée du document.
    pdf_name : nom exact du champ AcroForm.
    grist_column : colonne cible, si vous choisissez un mapping explicite.
    type : type logique indépendant du type PDF.
    required : obligatoire ou non.
    source : rempli par le client, généré, calculé ou réservé.
    deprecated : champ conservé pour lire les anciennes versions.
    introduced_in et removed_after : gestion de cycle de vie.

Par exemple :
  - id: client.ancien_nom
    pdf_name: client.ancien_nom
    grist_column: Client_AncienNom
    type: text
    deprecated: true
    replaced_by: client.nom
    read_only: true

## claude propose:

`---
form_id: demande-certification
version: 1.3.0            # semver : majeur = rupture de compatibilité
title: Demande de certification
fields:
  - id: demandeur.nom          # nom du champ PDF, ne change JAMAIS
    label: Nom                 # sert aussi de libellé accessible (TU)
    type: text
    required: true
    grist_column: Demandeur_Nom
    since: 1.0.0
  - id: demandeur.siret
    type: text
    pattern: "^\\d{14}$"
    grist_column: SIRET
    since: 1.2.0
  - id: demandeur.tel
    deprecated: 1.3.0
    replaced_by: demandeur.telephone
`---

Il faut compléter avec le modèle de formulaire pdf src\tem-404_formulaire\TEM-404_Formulaire_application_cadrage_V7_0.pdf

## Ce qui a été retenu :

Fusion simplifiée des deux propositions (le bloc `compatibility.*` de Perplexity est abandonné,
jugé prématuré) :

```yaml
---
form:
  id: tem-404
  title: "Titre du formulaire"
  schema_version: 1.0.0       # contrat de champs
  document_version: "2026.10" # version publiée du document
  language: fr-FR

pdf:
  output: "dist/TEM-404_v{document_version}.pdf"
  footer_label: "TEM-404 — version {document_version} (schéma {schema_version})"

grist:
  table: TEM_404

fields:
  - id: demandeur.nom
    label: "Nom"
    type: text                # text | checkbox | radio | choice
    grist_column: Demandeur_Nom
    required: true
    since: 1.0.0
  - id: demandeur.siret
    type: text
    maxlen: 14
    pattern: "^\\d{14}$"
    grist_column: SIRET
    since: 1.0.0
  - id: ancien_champ
    type: text
    deprecated: 1.1.0
    replaced_by: nouveau_champ
    read_only: true
---
```

Règles : un `id` n'est jamais renommé ni réutilisé ; `radio`/`choice` portent une liste
`options` ; `grist_column` est le mapping explicite consommé par le widget (pas par ce
pipeline de génération).

Voir `src/tem-404_formulaire/TEM-404.md` pour un exemple complet (contenu minimal
représentatif, la transcription intégrale des paragraphes A-K étant une tâche séparée).

# processus de générarion du formulaire au format pdf

Il faut décider entre la solution A et la solution B selon:
- les licences
- la maintenance (contraintes d'utiliser un fork ?)
- la complexité du processus (intuitivement, je pense qu'il faut tout faire en python pour avoir une chaîne simple)
- la complexité du pdf TEM-404 qui sert de modèle pour démarrer ce projet : import-externe\TEM-404_Formulaire_application_cadrage_V6_0.pdf, sachant que:
  - de nombreux paragraphes seront supprimés
  - il faut maintenir les boutons radio, les listes déroulantes
  - la mise en forme elle-même est secondaire, elle doit être correcte sans plus.

## solution A : ReportLab PDF Toolkit (open source)

Markdown/YAML
    ↓
Python
    ↓
ReportLab Platypus/canvas
    ↓
PDF avec champs AcroForm

## solution B : Playwright + pypdf

formulaire.md
    ↓
Python extrait le front matter
    ↓
Jinja2 génère formulaire.html
    ↓
Playwright produit le PDF visuel
    ↓
pypdf vérifie les champs du template
    ↓
assemblage ou injection des champs
    ↓
formulaire-final.pdf

ou encore:

Markdown + YAML
    ↓
Python
    ├── Markdown → HTML
    ├── HTML/CSS → PDF avec Playwright/Chromium
    ├── validation des champs avec pypdf
    └── ajout ou contrôle des champs AcroForm

## solution retenue :

**Solution A (ReportLab)**, en pur Python.

Rejet de la solution B (Playwright + pypdf) : dépendance lourde (Chromium, ~300 Mo, à
installer et maintenir) pour un gain de mise en forme non requis par les specs
("la mise en forme elle-même est secondaire, elle doit être correcte sans plus").
ReportLab est déjà installé dans l'environnement du projet et gère nativement les
champs AcroForm interactifs (`canvas.acroForm.textfield` avec `maxlen`, `checkbox`,
`radio`, `choice`) ainsi que le dessin de tableaux — une seule dépendance pure Python,
cohérente avec les autres scripts du dépôt (`import-externe/compare.py`,
`mcp-servers/annuaire_entreprises.py`).

**Point de design central** (répond à « facilement éditable ») : le corps markdown de
`TEM-404.md` (après le front matter) EST la mise en page — titres, paragraphes,
tableaux markdown standard, listes. Les emplacements de saisie sont marqués par un
jeton inline `{{field_id}}` référençant un `id` du front matter, y compris à
l'intérieur d'une cellule de tableau. Le script (`build_form.py` + paquet `formgen/`) :
1. sépare front matter / corps (`formgen/frontmatter.py`) ;
2. charge et valide la liste `fields` (`formgen/schema.py`) ;
3. parse le corps avec `markdown-it-py` (règle `table` activée) et le met en page
   avec un curseur vertical + pagination automatique (`formgen/layout.py`) ;
4. dessine texte/tableaux et pose les widgets `acroForm` aux emplacements `{{field_id}}`
   (`formgen/pdfgen.py`).

Ainsi, éditer le contenu (ajouter une ligne de tableau, reformuler un paragraphe) ne
touche jamais au code Python : le script repositionne les widgets automatiquement.
Le script exporte aussi `schemas/v{schema_version}.json` (la liste `fields` du front
matter), destiné à être chargé par le widget plus tard.

# gestion de retro-compatibilité

le widget grist src\tem-404_widget doit pouvoir lire un ancien formulaire.

## Claude a notamment mentionné:

"La compatibilité du widget avec les anciennes versions
Le PDF indique sa propre version. Le build ajoute deux champs cachés en lecture seule, _form_id et _form_version, et copie aussi ces informations dans les métadonnées du PDF. La version est également imprimée en pied de page.
Le widget embarque tous les schémas (v1.0.0.json, v1.2.0.json…). Il lit _form_version, charge le schéma correspondant, puis associe chaque champ à sa colonne grist_column.
Quatre règles de compatibilité :
un id n'est jamais renommé ni réutilisé ;
un champ ne se supprime pas, on le marque deprecated et on indique replaced_by pour reprendre les anciennes valeurs ;
ajouter un champ fait monter la version mineure ;
seule une rupture assumée fait monter la version majeure, et elle demande une mise à jour du widget.
Si la version est inconnue ou si _form_version manque, le widget affiche une erreur claire. C'est notamment le cas d'un PDF « aplati » par une impression en PDF : ses champs ont disparu."

## Perplexity a notamment mentionné:

"Principes :
    Ne jamais renommer silencieusement un ancien champ.
    Conserver les anciens noms en lecture.
    Ajouter les nouveaux champs comme optionnels au début.
    Faire les migrations dans le widget ou dans une couche de normalisation.
    Ne supprimer un champ qu’après une période de transition.
    Tester chaque version avec un PDF réel."

## Règles et architecture retenues pour assurer la rétrocompatibilité :

Reprend ce qui avait déjà été esquissé ci-dessus ("Claude a notamment mentionné") :

- Le PDF généré embarque deux champs AcroForm cachés en lecture seule, `_form_id` et
  `_form_version` (= `schema_version`), posés par `build_form.py`, plus un pied de page
  visible (`footer_label` du front matter).
- Un `id` de champ n'est jamais renommé ni réutilisé ; un champ retiré est marqué
  `deprecated: <version>` avec `replaced_by:` plutôt que supprimé (cf. l'exemple
  `demandeur.ancien_siret` dans `TEM-404.md`).
- Ajouter un champ → version mineure (`schema_version` monte, ex. 1.1.0). Rupture
  (retrait définitif, changement de type) → version majeure, nécessite une mise à
  jour du widget.
- Chaque génération exporte `schemas/v{schema_version}.json` (committé) — c'est ce
  fichier que le widget chargera selon le `_form_version` lu dans le PDF déposé, sans
  dépendre du contenu du markdown source.
- Un PDF aplati (champs AcroForm disparus à l'impression) est détectable par le widget
  du fait de l'absence de `_form_version` — ce pipeline se contente de l'embarquer
  correctement, la détection/erreur utilisateur est à la charge du widget (hors
  périmètre de ce chantier).