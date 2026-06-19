# CLAUDE.md — Grist Widgets (Certi-Trust FRANCE SAS)

## Contexte du projet

Widgets HTML personnalisés pour Grist, intégrés dans le système de gestion des examens et certifications de Certi-Trust FRANCE SAS. Chaque widget est un fichier `index.html` **autonome** (pas de build, pas de bundler) servi en statique.

## Architecture des widgets

Chaque widget suit cette structure :

```
src/<nom-widget>/
└── index.html          # Fichier unique, tout embarqué (CSS + JS inline)
```

### Squelette minimal d'un widget Grist

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <script src="https://docs.getgrist.com/grist-plugin-api.js"></script>
</head>
<body>
  <script>
    grist.ready({ requiredAccess: 'read table' });
    grist.onRecord(record => { /* ... */ });
  </script>
</body>
</html>
```

### API Grist — points clés

- `grist.ready({ requiredAccess })` — déclare le widget et ses permissions (`'none'`, `'read table'`, `'full'`)
- `grist.onRecord(fn)` — appelé quand la ligne sélectionnée change (vue ligne)
- `grist.onRecords(fn)` — appelé avec toutes les lignes de la table
- `grist.docApi.applyUserActions([...])` — écriture en base (requiert `'full'`)
- `grist.getTable()` — accès direct à la table liée
- Les colonnes sont mappées dans l'UI Grist via **Column Mapping**

## Widgets du projet

### `src/convocation-email/` — Envoi de convocations par e-mail

- Lit les données candidat depuis Grist (nom, prénom, email, examen, date, lieu)
- Génère un e-mail de convocation depuis un template
- Envoie via une API externe (à configurer : SMTP relay ou service transactionnel)
- Trace l'envoi (date, statut) en retour dans Grist

**Permissions Grist requises :** `'full'` (lecture + écriture du statut d'envoi)

### `src/exam-drag-drop/` — Glisser-déplacer examens vers sessions

- Affiche deux listes : examens écrits disponibles / sessions d'examen
- Drag & drop pour affecter un examen à une session
- Mise à jour immédiate dans Grist via `applyUserActions`

**Permissions Grist requises :** `'full'`

## Conventions de code

- **Pas de framework** (pas de React, Vue, etc.) — DOM vanilla uniquement
- **CSS inline** dans la balise `<style>` du fichier HTML
- **JS inline** dans la balise `<script>` du fichier HTML
- Nommage : kebab-case pour les fichiers et IDs CSS
- Langue de l'interface : **français**
- Pas de commentaires évidents — commenter uniquement les contraintes non-évidentes de l'API Grist

## Tests

Il n'y a pas de suite de tests automatisés. Tester manuellement :
1. Servir le fichier avec `npx serve src/<widget>/` ou équivalent
2. L'ouvrir dans Grist via l'URL locale (Grist doit être accessible)
3. Vérifier les cas nominaux et les cas d'erreur (colonne manquante, API indisponible)

## Licence

Propriété exclusive de **Certi-Trust FRANCE SAS**. Ne pas distribuer. Voir `LICENSE`.
