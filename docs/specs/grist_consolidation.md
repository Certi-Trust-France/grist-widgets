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

1. Dans un premier temps, il faut comparer :
   - catalogue de l'ANSSI
   - LIS_12
   - import-externe\20260929_liste.xlsx (produit par le directeur de centre)
ça a normalement déjà été fait, voir docs\grist_structure.md

2. Vérifier que GRIST contient les meilleures informations
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


