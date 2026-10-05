# Cahier des charges — formulaire TEM-404

**Projet :** Grist Widgets + formulaire — Certi-Trust FRANCE SAS  
**Widget :** `src/tem-404/`  
**Statut :** Spécification initiale  
**Date :** 2026-20-05

---

## 1. Contexte et objectif

Le processus de qualification commence chez Certi-Trust par la réception du formulaire TEM-404.
- Certi-Trust doit donc être en mesure de générer un formulaire pdf TEM-404
- le client remplit le formulaire
- le commercial dépose le fomrmulaire dans le widget TEM-404
- le widget vérifie si le client existe déjà, recherche les conflits, compare avec l'annuaire entreprise
- les données sont validées et enregistrées dans les différentes tables
Parmi les informations collectées, certaines servent au calcul de charge (calculer le nombre de JH et les répartir entre les évaluateurs).

Ces spécifications concernent la génération du formulaire TEM-404_vx_x.pdf, le widget et la table TEM_404.

Ces spécification ne concernent pas le time-calculator qui est l'étape suivante.

## 2. Utilisateurs cibles

- directeur de centre (mise à jour du TEM-404)
- Direction commerciale : exploitation du TEM-404 dans GRIST.

## 3. Modèle de données Grist

### Table principale : Entreprises

### Tables liées

- Contacts : comparer les contacts existants avec les nouveaux contacts
- sites : comparer les sites existants avec les nouveaux sites
- TEM-404 : données non incluses ailleurs

## 4. Fonctionnalités du widget

### 4.1 Interface principale du widget

Indiquer la version du TEM-404 acceptée. Favoriser la retro-compatibilité : il faut pouvoir déposer une ancienne version du TEM-404
Une zone dans laquelle glisser-déposer le TEM-404 au format pdf
Si entreprise existante : comparer les données siren, sites, etc.
Vérifier les données dans l'API entreprise
vérifier toutes les valeurs saisies
Les valider et remplir les tables

### 4.2 Actions

Valider toutes les informations et remplir les tables

### 4.3 Comportement aux cas d'erreur

indiquer si le pdf ne peut pas être lu

### 4.4 Critères d'acceptation

Les valeurs ont été correctement copiées dans les tables.

### 4.5 Copntraintes techniques

Perplexity mentionne :
"Intégration Grist

Pour le widget Grist, je recommande de ne pas coder directement les noms de colonnes dans le JavaScript.

Grist propose un mécanisme de column mapping : le widget déclare les champs attendus avec grist.ready, puis l’utilisateur associe ces champs aux colonnes réelles de la table. Le widget récupère ensuite les valeurs mappées avec grist.mapColumnNames. Cette approche résiste aux renommages de colonnes et permet de réutiliser le widget sur plusieurs tables."

## 5. Spécifications pour la génération du formulaire

Le TEM-404 est un formulaire pdf. Il est nommé selon son sa version : TEM-404_vx_x.pdf
Il doit exister en format md, près à être publié en pdf via un script pour faciliter la mise à jour.
Le TEM-404.md contient un front matter.
Le md, les formulaires générés, les scripts, css, etc, sont dans src\tem-404_formulaire
La stack, format du front matter, processus, sont dans src\tem-404_formulaire\tem-404_archi.md


