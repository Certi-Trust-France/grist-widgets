# Structure Grist — Certificats, cycles et évaluations

**Document Grist :** `Evaluations` (`7RViQWpLRdR51pWYH73DKF`)
**Mise à jour :** 2026-09-29

---

## 1. Principes

- **`LIS_12` est la référence** des certificats. Tout certificat délivré y est inscrit, et c'est Grist qui génère le certificat au format PDF à partir de cette table.
- Un cycle dure 3 ans (certification → surveillance à 18 mois → renouvellement). **Plusieurs certificats peuvent être émis au cours d'un même cycle** (réémission, changement de version, extension de périmètre) : **c'est le dernier qui fait foi**.
- La structure **`Cycles_services` ↔ `Evaluations` est conservée** : elle porte la planification (évaluation initiale, surveillance, renouvellement), y compris pour un cycle dont le certificat n'existe pas encore.
- Le fichier Excel « LIS-12 Certified Product, Service or Process Database » n'est plus la source de vérité. Il ne contient que les certificats PASSI (et 3 certificats eIDAS) et n'est pas toujours à jour. Il n'est pas modifié depuis Grist.

## 2. Tables

### 2.1 `LIS_12` — registre des certificats (référence)

Anciennement `Programmes_de_qualification2`, renommée le 2026-09-29. Page Grist : **LIS-12**.
(L'identifiant de table ne peut pas contenir de tiret : `LIS_12`.)

| Colonne | Type | Rôle |
|---|---|---|
| `Denomination` | Ref:Entreprises | Entité certifiée |
| `Programme` | Ref:Programmes | PASSI, PACS, PRIS, PDIS, PAMS, SecNumCloud |
| `Referentiel` | Ref:Documents_Referentiel | Version du référentiel au certificat (ex. `PASSI_2.0`, `PASSI_2.2`) |
| `Date_Delivrance` | Date | Date d'émission de ce certificat / de cette décision |
| `Qualifie_depuis_le` | Date | Début du cycle en cours |
| `Date_Fin` | Date | Fin de validité (fin du cycle) |
| `Debut_Cycle_Actuel` | Date (formule) | `DATEADD($Date_Fin, years=-3)` |
| `Niveau` | Choice | Elevé / Sansobjet |
| `Securite_nationale` | Bool | |
| `Qualifications` | RefList:Qualifications_List | Périmètre (activités / services) |
| `N_decision_ANSSI` | Numeric | N° de la décision de qualification ANSSI |
| `Lien_vers_la_decision_de_qualification` | Text | |
| `Version` | Any (formule) | |

**Origine des données actuelles :** import du catalogue ANSSI (une ligne par décision de qualification). La table brute `Programmes_de_qualification`, strictement identique, a été supprimée.

**Dates : ce sont celles des certificats Certi-Trust, pas celles de l'ANSSI.** Le 2026-09-29, les certificats PASSI présents dans le fichier Excel LIS-12 ont été alignés sur ce fichier (22 mis à jour, 11 ajoutés) : `Date_Delivrance` ← Issue date, `Date_Fin` ← Expiry date, `Qualifie_depuis_le` ← Registered since, `Referentiel` ← Standard. Les certificats absents du fichier (autres programmes, PASSI sans certificat Certi-Trust connu, renouvellements 2026 de Headmind et OWN) portent encore les dates du catalogue ANSSI et restent à vérifier.

**Règle de cycle :** un cycle commence à `Debut_Cycle_Actuel` (= `Date_Fin` − 3 ans), surveillance à + 18 mois, fin = `Date_Fin`. Quand un certificat expire la veille de l'anniversaire, le cycle démarre un jour avant l'émission ; c'est accepté.

**`Referentiel` :** renseigné le 2026-09-29 pour 25 lignes PASSI (21 × `PASSI_2.0`, 4 × `PASSI_2.2`) d'après le fichier LIS-12 et la colonne « Programme au certificat » de l'Excel de suivi. Ziwit, Algosecure (2.0) et Headmind (2.2) ont été déduits du cycle concerné. Restent vides : les programmes autres que PASSI (aucune version dans les sources) et les PASSI sans certificat Certi-Trust connu.

**Règle :** pour un couple (entreprise, programme), le certificat en vigueur est la ligne de `LIS_12` dont `Date_Delivrance` est la plus récente.

### 2.2 `Cycles_services` — cycles

| Colonne | Type | Rôle |
|---|---|---|
| `Denomination` | Ref:Entreprises | ⚠ à remplacer, voir § 3 |
| `Programme` | Ref:Programmes | |
| `Referentiel` | Ref:Documents_Referentiel | |
| `date_debut_cycle` | Date | Début du cycle (anciennement `date_certification`, renommée le 2026-09-29) |
| `Date_surveillance_certification` | Date (formule de déclenchement) | `date_debut_cycle + 18 mois` |
| `date_fin_certification` | Date (formule de déclenchement) | `date_debut_cycle + 3 ans` |
| `Prochaine_echeance` | Date (formule) | Prochaine date ≥ aujourd'hui |
| `eval_initiale` | RefList:Evaluations | |
| `eval_autres` | RefList:Evaluations | Surveillance, complémentaire |
| `eval_renouvellement` | Ref:Evaluations | |
| `certifie_depuis`, `date_Qualification_ANSSI`, `date_surveillance_qualifcation_ANSSI`, `date_fin_qualification_ANSSI`, `lien_qualification_ANSSI`, `Commentaires` | | Champs hérités |

Utilisée par le widget `src/cycles/`.

### 2.3 `Evaluations`

Évaluations réalisées par Certi-Trust (initiale, surveillance, renouvellement, complémentaire). Rattachées aux cycles par les colonnes `eval_*` de `Cycles_services`.

### 2.4 Tables liées

- `Entreprises` : entités juridiques (SIREN / SIRET vérifiés contre l'annuaire des entreprises).
- `Programmes` : liste des programmes (nom, couleur dans les widgets).
- `Documents_Referentiel` : référentiels et leurs versions (`PASSI_2.0`, `PASSI_2.2`, `PACS_1.0`, `PACS_1.1`, `PACS_2.0`, `PRIS_3.2`, `PDIS_2.0`, …).

## 3. Évolution à faire : rattacher les cycles aux certificats

> **TODO —** Les lignes de `Cycles_services` ne doivent plus faire référence à une entreprise mais **à un certificat de `LIS_12`**.

Cible :

```
Entreprises ──< LIS_12 (certificats) ──< Cycles_services ──< Evaluations
```

- Ajouter dans `Cycles_services` une colonne `Certificat` de type `Ref:LIS_12`.
- `Denomination` et `Programme` deviennent des formules : `$Certificat.Denomination`, `$Certificat.Programme`.
- Les dates du cycle se déduisent du certificat en vigueur (le dernier délivré), les dates saisies ne servant qu'aux cycles en préparation.
- Cas à traiter : cycle en préparation (évaluation initiale avant tout certificat), renouvellement (nouveau cycle ouvert alors que l'ancien certificat est encore valide).
- Adapter le widget `src/cycles/` en conséquence.

Migration non réalisée à ce jour.

## 4. Constats sur les données (analyse du 2026-09-29)

Comparaison détaillée : `import-externe/comparaison_cycles.csv` (non versionné).

- **PASSI** : les dates de certification de l'Excel de suivi (`20260929_liste.xlsx`, onglet « Par phase », colonnes Z/AA/AB) sont celles du fichier LIS-12 (31/32 identiques).
- **Qualification ANSSI** : les colonnes W/X/Y de l'Excel concordent avec `LIS_12` (40/41).
- **`Cycles_services`** contient souvent des dates ANSSI (délivrance de la qualification, 1 à 3 mois après le certificat) au lieu des dates de certification, des renouvellements 2026 non reportés (Algosecure, Ornisec, Ziwit), des lignes étiquetées PACS qui sont du PASSI (Accenture, Capgemini, Atos) et 24 lignes sans aucune date.
- Pour PACS, PRIS, PDIS, PAMS et SecNumCloud, aucune version de référentiel n'est indiquée dans les fichiers Excel.
