# Grist Widgets — Certi-Trust FRANCE SAS

Widgets HTML personnalisés pour [Grist](https://www.getgrist.com/), développés par **Certi-Trust FRANCE SAS** pour la gestion des examens et certifications.

> **Licence propriétaire exclusive.** Voir [LICENSE](./LICENSE).

---

## Widgets disponibles

| Widget | Dossier | Description |
|--------|---------|-------------|
| Convocation par e-mail | [`src/convocation-email/`](src/convocation-email/) | Envoi automatisé des convocations aux candidats depuis Grist |
| Glisser-déplacer examens | [`src/exam-drag-drop/`](src/exam-drag-drop/) | Affectation visuelle d'examens écrits dans des sessions d'examen |

---

## Structure du dépôt

```
grist_widgets/
├── src/
│   ├── convocation-email/     # Widget envoi de convocations
│   │   └── index.html
│   └── exam-drag-drop/        # Widget drag & drop sessions d'examen
│       └── index.html
├── docs/
│   ├── specs/                 # Cahiers des charges fonctionnels
│   └── studies/               # Études techniques et comparatives
├── CLAUDE.md                  # Instructions pour Claude Code
├── LICENSE                    # Licence exclusive Certi-Trust FRANCE SAS
└── README.md
```

---

## Intégration dans Grist

Chaque widget est un fichier `index.html` autonome. Pour l'ajouter dans Grist :

1. Héberger le fichier (GitHub Pages, serveur interne, etc.)
2. Dans Grist : **Ajouter un widget** → **Widget personnalisé** → coller l'URL
3. Configurer les colonnes mappées selon la documentation du widget

### API Grist utilisée

Les widgets communiquent avec Grist via `grist.ready()` et les événements `onRecord` / `onRecords`.

```js
grist.ready({ requiredAccess: 'read table' });
grist.onRecord(record => { /* traitement */ });
```

---

## Développement

Les widgets sont des fichiers HTML statiques, sans dépendance de build. Pour modifier :

1. Éditer le fichier `src/<widget>/index.html`
2. Tester en local via un serveur HTTP simple
3. Vérifier l'intégration avec une instance Grist de test

---

## Contact

**Certi-Trust FRANCE SAS** — contact@certi-trust.com
