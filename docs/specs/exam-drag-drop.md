# Cahier des charges — Widget Glisser-déplacer examens

**Projet :** Grist Widgets — Certi-Trust FRANCE SAS  
**Widget :** `src/exam-drag-drop/`  
**Statut :** Spécification initiale  
**Date :** 2026-06-19

---

## 1. Contexte et objectif

La planification des sessions d'examen nécessite d'affecter des examens écrits à des créneaux (sessions). Aujourd'hui cette opération se fait en éditant manuellement les cellules dans Grist. Ce widget offre une interface visuelle de type tableau kanban où les examens peuvent être glissés-déposés d'une colonne "Non affectés" vers une session d'examen, ou inversement.

## 2. Utilisateurs cibles

- Responsables de planification des examens

## 3. Modèle de données Grist

### Table principale : Examens écrits

| Colonne | Rôle | Type |
|---------|------|------|
| `id` | Identifiant unique | Entier |
| `Titre` | Intitulé de l'examen | Texte |
| `Candidat` | Nom du candidat | Texte |
| `Session_id` | FK vers la session affectée (nullable) | Référence / Entier |

### Table liée : Sessions d'examen

| Colonne | Rôle | Type |
|---------|------|------|
| `id` | Identifiant unique | Entier |
| `Nom_session` | Nom ou code de la session | Texte |
| `Date` | Date de la session | Date |
| `Lieu` | Lieu | Texte |
| `Capacite_max` | Nombre maximum de candidats | Entier |

## 4. Fonctionnalités

### 4.1 Interface principale

- Colonne de gauche : **Examens non affectés** (Session_id = null)
- Colonnes suivantes : la **session d'examen** qui a été sélectionnée dans la tables des sessions.
- Chaque carte examen affiche : entreprise, nom et prénom du candidat, intitulé, éventuellement date souhaitée

### 4.2 Drag & drop

- Glisser une carte depuis "Non affectés" vers la session → met à jour `Session_id`
- Glisser vers "Non affectés" → remet `Session_id` à null
- Feedback visuel pendant le drag (ombre, zone de dépôt mise en évidence)

### 4.3 Indicateurs de capacité

- Chaque colonne-session affiche : $Places_disponibles (que j'ai converti en entier)
- Couleur d'alerte si $Places_disponibles = 0 (rouge) ou $Places_disponibles = 1 (orange)

### 4.4 Filtres

- Barre de recherche pour filtrer les examens par candidat ou entreprise

### 4.5 Actions

- Chaque drag & drop déclenche un `applyUserActions` immédiat dans Grist
- Pas de mode "brouillon" — les modifications sont directes

## 5. Contraintes techniques

- Drag & drop HTML5 natif (API `draggable`, `dragstart`, `dragover`, `drop`) — pas de bibliothèque externe
- Permissions Grist `'full'` requises
- Le widget lit les deux tables via le Column Mapping Grist
- Rendu réactif aux changements extérieurs (un autre utilisateur modifie les données → le widget se rafraîchit)

## 6. Comportement aux cas d'erreur

| Situation | Comportement attendu |
|-----------|---------------------|
| Session pleine | Dépôt refusé + message d'alerte |
| Erreur écriture Grist | Annulation du déplacement visuel + message d'erreur |
| Table sessions vide | Message "Aucune session disponible" |
| Table examens vide | Message "Aucun examen à planifier" |

## 7. Critères d'acceptation

- [ ] Un examen glissé vers une session a son `Session_id` mis à jour dans Grist
- [ ] Un examen glissé vers "Non affectés" a son `Session_id` remis à null
- [ ] L'indicateur de capacité se met à jour après chaque dépôt
- [ ] Le dépôt dans une session pleine est refusé avec feedback visuel
- [ ] La recherche filtre les cartes en temps réel
- [ ] Le widget se met à jour si les données changent depuis un autre client Grist
