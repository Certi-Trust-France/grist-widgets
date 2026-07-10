# Cahier des charges — Widget Demande d'un devis examens

**Projet :** Grist Widgets — Certi-Trust FRANCE SAS  
**Widget :** `src/demande-devis-examens/`  
**Statut :** Spécification initiale  
**Date :** 2026-07-10

---

## 1. Contexte et objectif

La planification des sessions d'examen nécessite de faire signer un devis à l'entreprise.
Le candidat s'inscrit à un examen via un formulaire. Le planificateur des examens crée les examens puis envoie à la direction commerciale la demande d'examens. La direction commerciale fait signer le devis et renseigne GRIST.

## 2. Utilisateurs cibles

- Responsables de planification des examens
- Direction commerciale

## 3. Modèle de données Grist

### Table principale : Examens écrits

| Colonne | Rôle | Type |
|---------|------|------|
| `id` | Identifiant unique | Entier |
| `Titre` | Intitulé de l'examen | Texte |
| `Candidat` | Nom du candidat | Texte |
| `Session_id` | FK vers la session affectée (nullable) | Référence / Entier |
TODO: à compléter

### Table liée : Purchase orders

| Colonne | Rôle | Type |
|---------|------|------|
| `id` | Identifiant unique | Entier |
TODO: à compléter

## 4. Fonctionnalités

### 4.1 Interface principale

TODO

### 4.5 Actions

TODO

## 5. Contraintes techniques

TODO

## 6. Comportement aux cas d'erreur

TODO

## 7. Critères d'acceptation

TODO
