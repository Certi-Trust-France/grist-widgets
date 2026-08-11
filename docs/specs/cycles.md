# Cahier des charges — Widget Demande d'un devis examens

**Projet :** Grist Widgets — Certi-Trust FRANCE SAS  
**Widget :** `src/cycles/`  
**Statut :** Spécification initiale  
**Date :** 2026-08-11

---

## 1. Contexte et objectif

Evaluations(xx).grist contient une table CYCLES_SERVICES. Il s'agit de cycles d'évaluations. Un entreprise demande à être qualifiée PASSI ou PACS ou PRIS, etc à une date t. Certi-Trust fait l'évaluation puis elle est certifiée à une date date_certification. Elle doit faire une évaluation de surveillance avant date_surveillance = date_certification + 18 mois puis une évaluation de renouvellement avant la date date_fin_certification = date_certification + 3 ans. elle est de nouveau certifiée à une date t4 qui devient le t0 d'un nouveau cycle.
Il est possible d'attribuer des évaluations de la table EVALUATIONS aux cycles : eval_initiale eval_autres (surveillance ou complémentaire) et eval_renouvellement.

## 2. Utilisateurs cibles

- planificateurs, commerciaux, directeur de centre

## 3. Modèle de données Grist

### Table principale : CYCLES_SERVICES

### Table secondaire : EVALUATIONS

## 4. Fonctionnalités

### 4.1 Interface principale

un tableau-planning :
- une ligne par cycle
- de 5 à 6 années de large
- centré sur la date du jour
- bicolor : bleur clair années paires, bleu foncé années impaires
- le cycle en gris marqué par trois traits jaunes : dates certification, surveillance et renouvellement
- avant le cycle, afficher le programme dans un rectangle aux coins arrondis avec le code couleur de la table PROGRAMMES, Nom_du_programme.
- Si le cycle contient des évaluations, afficher sur le planning à la date de Date_Debut de l'évaluation 'EVA' dans un rectangle arrondi, fond jaune. Quand on survole l'évaluation, afficher son libellé.

### 4.5 Actions

trois tris possibles :
- par ordre alphabétique des entreprises
- par ordre chronologiue des dates de certification
- par ordre chronologique de la prochaine échéance
filtres :
- par programme (PASSI, PACS, PRIS, etc)

## 5. Contraintes techniques

TODO

## 6. Comportement aux cas d'erreur

TODO

## 7. Critères d'acceptation

TODO
