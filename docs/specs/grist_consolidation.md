---
titre: consolidation des données GRIST pour en faire un outil opérationnel
date: 20260930
---
# Consolidation des données GRIST
l'objectif est de tout stocker dans GRIST et d'en faire un outil de planification opérationnelle.

## Origine des données

### PASSI
En PASSI, les opérations sont synchronisées sur les certificats émis par Certi-Trust : import-externe\LIS-12 Certified Product, Service or Process Database.xlsx
La référence est la date de début de qualification : 
- 18 mois après, il faut faire une proposition commerciale et planifier une évaluation de surveillance.
- 3 ans après, meême chose pour le renouvellement
Le renouvellement doit conduire à produire un nouveau certificat et un nouveau cycle de 3 ans

### PACS, PRIS, PDIS, Secnumcloud
Jusqu'au 30/09/2026, Certi-Trust n'émettait pas de certificat.
La référence est la date_fin_qualification du catalogue de l'ANSSI : import-externe\202609_anssi_services_qualifies.csv
- cette date est la date où il faut planifier le renouvellement
- 3 ans avant : c'est le début de cycles
- 18 mois avant (après le début de cycle) c'est la date de surveillance
Toutes ces informations ont été consolidées dans import-externe\20260929_liste.xlsx

## destination des données dans GRIST

Tout est expliqué dans docs\grist_structure.md

## tâches à exécuter

1. ✅ terminée — Dans un premier temps, il faut comparer :
   - catalogue de l'ANSSI
   - LIS_12
   - import-externe\20260929_liste.xlsx (produit par le directeur de centre)
ça a normalement déjà été fait, voir docs\grist_structure.md

2. ✅ terminée Vérifier que GRIST contient les meilleures informations dans Cycles
Voir le dernier paragraphe de docs\grist_structure.md
Il faut bien aligner les cycles sur les dates de fin de qualification (sauf pour PASSI)

3. Une fois que GRIST est consolidé, me dire les écarts avec import-externe\20260929_liste.xlsx pour que je puisse reboucler avec le directeur de centre.
oui
4. TODO: pourquoi dans LIS_12 :
ASF ACT DIGITAL	PASSI	PASSI_2.0
Intrinsec Sécurité 	PASSI	PASSI_2.0
MVE	PASSI	PASSI_2.0
Monaco Cyber Sécurité	PASSI	PASSI_2.0
Headmind Partners France	PASSI	PASSI_2.0
Apixit	PASSI	PASSI_2.0
Ornisec	PASSI	PASSI_2.2
n'ont pas de Qualifications ni de niveau ni de sécurité nationale ?

### Tâche complexe sur les cycles
Les cycles ne vont plus faire référence à une entreprise mais à LIS-12. Normalement les dates sont les mêmes puisque nous avons consolidés.
Certificat renseigné :
Le programme et la date_debut_cycle et denomination doivent être une référence à la ligne LIS-12.
PAs de certificat renseigné :
Si pas de référence dans LIS-12, la dénomination et le programme doivent être une référence à l'évaluation présente dans eval_initiale ou eval_autres ou eval_renouvellement.
1. ✅ terminée - commençons par renseigner le certificat si tu le trouves
   - ajoute une colonne certificat
   - Si tu trouves le certificat, tu y fais référence.
   - rends-moi compte
2. ✅ terminée - formules
   - remplace date_debut_cycle par une formule qui pointe vers la date deubt_cycle_actuel de LIS-12
   - si pas de certificat, il faut qu'il y ait une eval initiale
     - Pour ceux qui ont une éval initiale tu renseignes la **date defin** :
       - 1. la date_terminee de l'éval sinon
       - 2. la date du lot  "Rédaction du rapport" si présente dans les lots, sinon
       - 3. la date_fin_prevue sinon
       - 4. la date de la "Journée de lancement" si présente dans les lots + 3 mois, sinon
       - 5. la date prévue début + 3 mois
   - sinon on ajoute une colonne date_debut_anssi et on met la date d'expiration de l'anssi moins 3 ans (pour Cloud Temple on verra plus tard)

## amélioration du widget 1
- L'étiquette évaluation doit commencer à :
  - 1. la date de la "Journée de lancement" ou
  - 2. à la Date_Debut_prevue
- et se terminer à la **date de fin**, comme précédemment.
- couleur :
  - pas de RE : orange
  - RE mais pas terminée : vert
  - terminée : gris
- contenu : libellé de l'évaluation tronquée à 10 caractère
- en survolant : libellé complet
- ✅ terminée - Cycles : en gris comme existant si certificat, en hachuré (type rubalise gris et transparent) si future cycle quand l'évalaution initiale sera terminée.

### Tâche complexe de consolidation des évaluations
TODO: consolider la table évaluations avec import-externe\20260929_liste.xlsx ou version plus récente sur le sharepoint.

### Tâche complexe de consolidation des propositions commerciales
Consolider la table Purchase_orders avec import-externe\Synthese_propositions_factures_ANSSI_selection_reel.xlsx ou une extraction doolibar plus récente

### amélioration du widget 2
Afficher les propales sur les cycles.

