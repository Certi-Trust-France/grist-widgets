# Cahier des charges — Widget Planning des évaluations

**Projet :** Grist Widgets — Certi-Trust FRANCE SAS  
**Widget :** `src/planning/`  
**Statut :** Spécification initiale  
**Date :** 2026-07-17

---

## 1. Contexte et objectif

Le widget GRIST de calendrier ne répond pas au besoin.
Je souhaite créer un widget pour observer sur un planning journalier sur le modèle de docs\specs\Plan_de_charge_Certitrust_V11.xlsx :
- en lignes :
  - les mois, les semaines, jour de mois et de semaine
  - les we et jours fériés en France
- en colonnes :
  - les évaluateurs, s'ils sont salariés de Certi-Trust ou non
- les cases doivent contenir :
  - le client
  - la couleur du programme (PASSI, PACS, PRIS, PDIS, PAMS, SECNUMCLOUD)
Les sources de données sont les tables de GRIST :
- fichier de sctructure sqlite GRIST docs\specs\Evaluations(36).grist
- tables :
  - des Lots_d_évaluation (qui contient les jour/homme)
  - des Evaluateurs (en colonne)
- mais aussi les tables :
  - des évaluations : évaluations
  - des entreprises : Entreprises
