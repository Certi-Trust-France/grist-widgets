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

Le TEM-404 comporte trois groupes d'informations, qui ne sont pas stockées de la même façon :

1. **Informations d'entreprise** (structure déjà/bientôt présente dans Grist) : nom, SIREN/SIRET,
   sites, contacts, systèmes d'information. Écrites dans les tables structurées ci-dessous.
2. **Informations utiles au calcul de charge** (paragraphes B, C, D, E) : consommées par le
   time-calculator (hors périmètre de ce chantier). Stockées en JSON (`TEM_404.Json_Utile`).
3. **Informations à archiver pour information** (B.2, B.3) : pas d'usage de calcul identifié,
   conservées pour trace. Stockées avec le groupe 2 dans `TEM_404.Json_Utile`.

Dans le pipeline de génération (`src/tem-404_formulaire/TEM-404.md`), un champ appartient au
groupe 1 s'il déclare `grist_table` dans le front matter ; sinon il part uniquement en JSON
(`TEM_404.Json_Complet` dans tous les cas, `TEM_404.Json_Utile` en plus s'il n'a pas de
`grist_table`).

### Table principale : Entreprises

### Tables liées

- `Contacts` : comparer les contacts existants avec les nouveaux contacts. `Programmes_Responsable`
  (RefList:Programmes) et `Programmes_Examens` (RefList:Programmes, limité par convention à
  {PASSI, PACS, PRIS}) remplacent les anciens booléens `Responsable_de_programme` /
  `Responsable_examens` (conservés pour l'instant en parallèle, migration des données déjà faite).
- `Sites` : comparer les sites existants avec les nouveaux sites.
- `Systemes_Information` (nouvelle table) : SI des entreprises évaluées — `Entreprise` (Ref),
  `Nom`, `Classification` (Choice : NP / DR Classe 1 / DR Classe 2), `Date_Homologation`,
  `Programmes` (RefList), `Sites` (RefList, à restreindre en pratique aux sites de la même
  entreprise).
- `TEM_404` (nouvelle table) : un enregistrement par dossier déposé — `NumTEM404`,
  `Date_Reception`, `Version` (= `_form_version` du PDF), `Entreprise` (Ref, lien de confort),
  `Json_Complet` (toutes les valeurs extraites), `Json_Utile` (groupes 2+3 uniquement — ce que
  lira le time-calculator). Ces deux colonnes JSON ne doivent être modifiées que par le widget.

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

**Décision retenue (2026-10-07) :** pas de column mapping générique pour ce widget — noms de
colonnes codés en dur, comme le reste des widgets du dépôt (`exam-drag-drop`,
`convocation-ecrits`). La résistance aux renommages visée par la recommandation est déjà assurée
autrement : chaque champ du formulaire porte son `grist_column`/`grist_table` explicite dans le
schéma JSON versionné (`src/tem-404_formulaire/schemas/v{version}.json`), qui est la source de
vérité consommée par le widget.

### 4.6 État d'avancement

- Pipeline de génération (`src/tem-404_formulaire/`) : fonctionnel, étendu avec `grist_table` par
  champ et des champs représentatifs pour les 3 groupes d'informations (§3).
- Schéma Grist : `Systemes_Information` et `TEM_404` créés ; `Contacts.Programmes_Responsable` /
  `Programmes_Examens` ajoutées et migrées depuis les anciens booléens (conservés pour l'instant,
  suppression différée).
- **Widget `src/tem-404_widget/` : développé** — glisser-déposer du PDF, lecture AcroForm via
  pdf-lib, numérotation `[année]_TEM-404_[####]`, rapprochement GRIST (SIREN/SIRET exact + nom
  flou par distance de Levenshtein) et annuaire des entreprises (fallback SIRET → SIREN → nom),
  écriture dans `TEM_404` uniquement (`Entreprise` en lien de confort). N'écrit pas encore dans
  `Entreprises`/`Sites`/`Systemes_Information`/`Contacts` (décision explicite, chantier séparé).
- **Contenu transcrit depuis le PDF modèle v7.1** (schéma v1.3.0) : section A (dénomination,
  SIREN/SIRET, adresse décomposée, téléphone, site internet — pas de n° TVA), A.2 (les deux
  contacts réels : représentant légal, facturation/achat), et B en entier (B. Nature de la
  demande pour les 6 programmes, B.2 Historique de qualification, B.3 Statut ANSSI). Les anciens
  champs de démonstration (`historique.programme1.*`, `type_evaluation`, `archive.b2/b3.*`,
  `contact.1.*`, `demandeur.adresse`/`adresse_siege`) sont dépréciés avec `replaced_by`. Sections
  C à J (hors G, toujours en extrait de démo) restantes à transcrire.

## 5. Spécifications pour la génération du formulaire

Le TEM-404 est un formulaire pdf. Il est nommé selon son sa version : TEM-404_vx_x.pdf
Il doit exister en format md, près à être publié en pdf via un script pour faciliter la mise à jour.
Le TEM-404.md contient un front matter.
Le md, les formulaires générés, les scripts, css, etc, sont dans src\tem-404_formulaire
La stack, format du front matter, processus, sont dans src\tem-404_formulaire\tem-404_archi.md


