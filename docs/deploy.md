# Déploiement des widgets Grist

**Repo :** https://github.com/Certi-Trust-France/grist-widgets  
**Hébergement :** GitHub Pages (branche `main`, répertoire racine)

---

## 1. URL des widgets en production

Chaque widget est un fichier `index.html` autonome servi statiquement par GitHub Pages.

| Widget | Source Grist | URL |
|--------|-------------|-----|
| Planning | `Lots_audit` | `https://certi-trust-france.github.io/grist-widgets/src/planning/` |
| Drag & drop examens | `Sessions_examens_ecrits` | `https://certi-trust-france.github.io/grist-widgets/src/exam-drag-drop/` |
| Cycles de certification | `Cycles_services` | `https://certi-trust-france.github.io/grist-widgets/src/cycles/` |
| Demande de devis | — | `https://certi-trust-france.github.io/grist-widgets/src/demande-devis-examens/` |
| CR oral | — | `https://certi-trust-france.github.io/grist-widgets/src/cr-oral/` |
| Convocation e-mail | — | `https://certi-trust-france.github.io/grist-widgets/src/convocation-email/` |
| Planning convocations écrits | `Sessions_examens_ecrits` | `https://certi-trust-france.github.io/grist-widgets/src/convocation-ecrits/` |

> Les URL sont stables : un widget référencé dans Grist n'a pas besoin d'être mis à jour lors d'un déploiement — il suffit de pousser sur `main`.

---

## 2. Activer GitHub Pages (première fois)

1. Aller sur https://github.com/Certi-Trust-France/grist-widgets/settings/pages
2. **Source** → `Deploy from a branch`
3. **Branch** → `main` / `/ (root)`
4. Cliquer **Save**

GitHub Pages est alors actif à l'adresse `https://certi-trust-france.github.io/grist-widgets/`.  
Le premier déploiement prend 1 à 2 minutes.

---

## 3. Déployer une modification

Tout `push` sur `main` déclenche automatiquement un redéploiement :

```bash
git add src/<widget>/index.html
git commit -m "feat: description de la modification"
git push
```

Le widget est en ligne en moins d'une minute.

---

## 4. Référencer un widget dans Grist

1. Ouvrir la page Grist cible.
2. Cliquer **Ajouter un widget** → **Widget personnalisé**.
3. Coller l'URL du widget (tableau ci-dessus).
4. Choisir la **source de données** (table Grist à lier).
5. Configurer le **Column Mapping** si le widget en a besoin.
6. Définir les **permissions** requises (`read table` ou `full`).

---

## 5. Développement local

Servir le widget localement pour tester avant de pousser :

```bash
npx serve src/<widget>/
# puis ouvrir Grist et pointer le widget vers http://localhost:3000
```

> Grist doit être accessible depuis le navigateur pour que l'API `grist-plugin-api.js` fonctionne. En local, utiliser Grist Desktop ou une instance Grist accessible en réseau.

---

## 6. Ajouter un nouveau widget

```bash
mkdir src/<nom-widget>
# créer src/<nom-widget>/index.html (voir CLAUDE.md pour le squelette)
git add src/<nom-widget>/
git commit -m "feat: nouveau widget <nom>"
git push
```

L'URL du widget sera automatiquement :  
`https://certi-trust-france.github.io/grist-widgets/src/<nom-widget>/`

Ajouter la ligne correspondante dans le tableau de la section 1.

---

## 7. Vérifier un déploiement

- **État GitHub Actions** : https://github.com/Certi-Trust-France/grist-widgets/actions  
  (onglet *pages build and deployment*)
- **Test rapide** : ouvrir l'URL du widget dans un navigateur — une page blanche ou un message "Widget Grist non connecté" est normal hors de Grist.
