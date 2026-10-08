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
  flou par distance de Levenshtein) et annuaire des entreprises (sur clic uniquement, bouton
  dédié ; fallback SIRET → SIREN → nom), écriture dans `TEM_404` (`Entreprise` en lien de
  confort). **Écrit aussi désormais dans `Entreprises` et `Sites`** (le site "Siège"
  uniquement) via trois boutons dans le cadre GRIST : « Créer un nouveau client » (AddRecord),
  « Remplacer par les données TEM-404 » / « ... par les données annuaire » (UpdateRecord sur
  l'entreprise GRIST actuellement affichée), chacun avec confirmation avant écriture. Les sites
  2 à 6 restent hors périmètre (chantier séparé).
- **Section A.3 — Contacts (widget v1.8.0) : consolidation TEM-404 ↔ GRIST.** Une même
  personne peut apparaître plusieurs fois dans le PDF (représentant légal, facturation,
  chef de projet d'un ou plusieurs des 6 programmes B.1-B.6, responsable examens
  PASSI/PACS/PRIS) ; le widget les rassemble en une fiche par personne (clé de
  dédoublonnage : courriel, à défaut prénom+nom) et affiche, dans la grille générique « A.3
  — Contacts », deux cadres côte à côte : « TEM-404 » (une sous-carte éditable par contact
  consolidé — case « à copier dans GRIST » cochée par défaut, coordonnées, « Représentant
  légal »/« Facturation », 6 cases « Responsable programme », 3 cases « Responsable
  examens ») et « GRIST » (contacts existants de l'entreprise actuellement rapprochée,
  lecture seule). Bouton « Copier les contacts cochés dans GRIST » : pour chaque contact
  coché, rapproche un contact GRIST existant (courriel, sinon nom+prénom) et fait un
  `UpdateRecord`/`AddRecord` sur `Contacts` — **remplace** `Programmes_Responsable` /
  `Programmes_Examens` (RefList, ids résolus dynamiquement depuis `Programmes.Nom_du_programme`,
  jamais figés en dur) et `Representant_legal`/`Facturation` (Bool) par l'état des cases à
  cocher, avec confirmation avant écriture. Nécessite une entreprise GRIST rapprochée
  (sinon message d'erreur, aucun lien `Entreprise` possible). N'écrit pas les anciens
  booléens `Responsable_de_programme`/`Responsable_examens` (supersédés par les RefList).
  Les RefList sont écrites au format CellValue brut `['L', id1, id2, ...]` —
  `applyUserActions` n'encode pas automatiquement un tableau nu, qui est mal décodé côté
  GRIST et produit `#KeyError`/`#IndexError` dans la cellule (bug rencontré et corrigé en
  v1.8.1).
- **Sections A.2 — Sites et F — Systèmes d'information (widget v1.9.1) : même principe
  TEM-404 ↔ GRIST que les contacts, en plus simple (pas de consolidation, les 6 sites et les
  3 SI du PDF sont déjà des slots numérotés distincts).**
  - **A.2 — Sites** : un sous-cadre par site **2 à 6** dans le cadre « TEM-404 » (Site 1 -
    Siège est exclu de cette section : il est déjà traité séparément, voir ci-dessous) —
    titre « Site 2 »… case « à copier dans GRIST » (cochée par défaut pour tout site non
    vide), champs nom/adresse/adresse 2/code postal/commune/pays (`f.site{n}.*`, édition via
    la délégation générique déjà en place). Cadre « GRIST » : sites existants de l'entreprise
    rapprochée, lecture seule. Bouton « Copier les sites cochés dans GRIST » (sites 2-6
    uniquement) : rapproche un site GRIST existant par `Nom_site` et fait un
    `UpdateRecord`/`AddRecord` sur `Sites`.
  - **Site 1 - Siège : traité directement dans les cadres principaux**, pas dans la section
    A.2. Cadre « TEM-404 » principal (`col1Fields`) : intitulé « Site 1 - Siège : » affiché
    au-dessus du champ « Adresse 1 » (rappel que ces champs `demandeur.adresse*` sont aussi
    les données du site 1). Cadre « GRIST » principal (`gristBox`) : sous Nom/SIREN/SIRET,
    intitulé « Site 1 - Siège : » puis adresse 1/2, code postal, ville, pays du site GRIST où
    `Siege=true` pour l'entreprise rapprochée (lecture seule, chargé à part via
    `loadExistingGristSites`). Les boutons « Remplacer par les données TEM-404 »/« ... par
    les données annuaire » (déjà existants, `upsertSiege`) mettent à jour ce même site
    Siège ; ce cadre se rafraîchit automatiquement après leur clic.
  - **F — Systèmes d'information** : un sous-cadre par SI (1 à 3), case « à copier dans
    GRIST » (cochée par défaut si un nom ou un programme est renseigné), champs nom/
    classification/date d'homologation + cases à cocher programmes/sites concernés. Cadre
    « GRIST » : SI existants de l'entreprise rapprochée, lecture seule. Bouton « Copier les SI
    cochés dans GRIST » (ignore les SI sans nom) : `UpdateRecord`/`AddRecord` sur
    `Systemes_Information`, `Programmes`/`Sites` en RefList (`['L', ...]`, ids résolus
    dynamiquement — `Sites` par correspondance de nom avec les sites déjà présents dans
    GRIST, donc à copier après les sites pour de meilleurs résultats ; le site 1 - Siège y
    est éligible via sa correspondance `Siege=true`), `Date_Homologation` convertie depuis le
    texte libre du PDF via le même parsing multi-format que `Date_Reception`.
  - Ces sections nécessitent elles aussi une entreprise GRIST rapprochée.
  - **Ordre d'affichage de la grille générique** : forcé pour que « A.2 — Sites » précède
    toujours « A.3 — Contacts » (`GROUP_ORDER_PRIORITY`), indépendamment de l'ordre naturel
    des champs dans `schema.fields` (les champs `f.site*` sont déclarés tard dans le
    formulaire, ce qui plaçait sinon cette section en toute fin de grille). Les en-têtes
    « B — PROGRAMME » portent désormais leur numéro de paragraphe (« B.1 — PASSI » …
    « B.6 — SecNumCloud »).
  - **Correction d'affichage** : les cases à cocher de la grille générique (B.1-B.6, F — SI,
    « Autres »...) héritaient à tort du padding/bordure des champs texte, ce qui décalait
    visuellement le carré de la case par rapport à son libellé — réservé désormais aux
    champs non-checkbox.
- **Contenu transcrit depuis le PDF modèle v7.1 — formulaire entier, schéma remis à plat en
  v1.0.0** (296 champs AcroForm) : le formulaire n'ayant encore jamais été utilisé par un client,
  tous les champs de démonstration/intermédiaires et leurs `deprecated`/`replaced_by` ont été
  supprimés (pas de compatibilité ascendante à maintenir) ; tous les champs restants portent
  `since: 1.0.0`. Structure finale : A.1 (dénomination, SIREN/SIRET, téléphone, site internet —
  pas de n° TVA, pas d'adresse directe), **A.2 Sites** (jusqu'à 6 sites ; la ligne "Site 1 - Siège"
  porte l'adresse de l'organisation via `demandeur.adresse1/2/code_postal/ville/pays`, `Nom du
  site` par défaut "Siège"), A.3 Contacts (représentant légal, facturation/achat), B en entier (6
  programmes + matrice "sites concernés par programme", B.7 Historique, B.8 Statut ANSSI —
  `Version`/`Niveau`/`Type de demande` en listes déroulantes, ce dernier aligné sur
  `Evaluations.Type_d_evaluation` sans "Complémentaire"), C (C.1-C.3 : cases à cocher libellées par
  leur seule abréviation), D, E, F (ex-G, 3 SI × 6 programmes × 6 sites), G (planification), H
  (liste de documentation), I (déclaration). Groupe 1 (écriture structurée future) couvre A.1/A.3
  (`Entreprises`/`Contacts`) et F (`Systemes_Information` ; les cases à cocher programme/site n'ont
  pas d'équivalent colonne unique et restent JSON-only).
- **Widget** : code inchangé par ce nettoyage (`WIDGET_VERSION` reste à sa valeur courante,
  indépendante de la version du schéma du formulaire) — il charge dynamiquement
  `schemas/v{version}.json` selon le `_form_version` lu dans le PDF déposé, donc aucune mise à jour
  n'était nécessaire pour accompagner le passage à la v1.0.0.

## 5. Spécifications pour la génération du formulaire

Le TEM-404 est un formulaire pdf. Il est nommé selon son sa version : TEM-404_vx_x.pdf
Il doit exister en format md, près à être publié en pdf via un script pour faciliter la mise à jour.
Le TEM-404.md contient un front matter.
Le md, les formulaires générés, les scripts, css, etc, sont dans src\tem-404_formulaire
La stack, format du front matter, processus, sont dans src\tem-404_formulaire\tem-404_archi.md


