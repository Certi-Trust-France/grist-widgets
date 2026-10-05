---
objet: architecture du processus de génération du formulaire TEM-404 depuis un fichier md
maj: 2026-10-05
---
# stack
- vscode

# format du front matter du tem-404 au format md

perplexity propose :
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

claude propose:
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

Il faut compléter avec le modèle de formulaire pdf import-externe\TEM-404_Formulaire_application_cadrage_V6_0.pdf

écrire ci-dessous ce qui est retenu:

**à compléter par Claude**

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

# gestion de retro-compatibilité

le widget grist src\tem-404_widget doit pouvoir lire un ancien formulaire.

Claude a notamment mentionné:
"La compatibilité du widget avec les anciennes versions
Le PDF indique sa propre version. Le build ajoute deux champs cachés en lecture seule, _form_id et _form_version, et copie aussi ces informations dans les métadonnées du PDF. La version est également imprimée en pied de page.
Le widget embarque tous les schémas (v1.0.0.json, v1.2.0.json…). Il lit _form_version, charge le schéma correspondant, puis associe chaque champ à sa colonne grist_column.
Quatre règles de compatibilité :
un id n'est jamais renommé ni réutilisé ;
un champ ne se supprime pas, on le marque deprecated et on indique replaced_by pour reprendre les anciennes valeurs ;
ajouter un champ fait monter la version mineure ;
seule une rupture assumée fait monter la version majeure, et elle demande une mise à jour du widget.
Si la version est inconnue ou si _form_version manque, le widget affiche une erreur claire. C'est notamment le cas d'un PDF « aplati » par une impression en PDF : ses champs ont disparu."
