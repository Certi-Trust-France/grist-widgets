# Cahier des charges — Widget Convocation aux examens écrits

**Projet :** Grist Widgets — Certi-Trust FRANCE SAS  
**Widget :** `src/convocation-ecrits/`  
**Statut :** Spécification initiale  
**Date :** 2026-08-11

---

## 1. Contexte et objectif

Le gestionnaire des examens écrits doit envoyer des convocations aux candidats inscrits. Aujourd'hui cette opération est manuelle (copier-coller, envoi un par un). Ce widget permet :
- de planifier la session d'examens en programmant les horaires des examens
- d'envoyer des convocations directement depuis Grist, en un clic, à partir des données de la page Convocations écrits.

## 2. Utilisateurs cibles

- Gestionnaire des examens Certi-Trust
- Surveillants de session

## 3. Données en entrée

table examens écrits
table sessions_examens_ecrits

## 4. Fonctionnalités

### 4.1 Vue principale

- affiche un planning de la journée d'examens sur 7 colonnes, une colonne par candidat (normalement il y a maximum 6 candidats mais on se réserve une marge)
- sous le nom du candidat, la liste des "Qualification" avec un champ heure de début éditable à côté (qui correspond à l'heure de la colonne date_heure de l'examen)
- sous la liste, le planning horaire de la journée avec des rectangles arrondis et la qualification inscrite dedans
- les horaires des examens sont 09h30-12h30 et à partir de 13h
- les heures paires sont en bleu clair et les heures impaires en bleu foncé (mêmes couleurs que les années de src/cycles/index.html)
- un bouton dans le bandeau supérieur permet de calculer automatiquement les horaires des examens planifiés ce jour selon les règles ### 4.3 calcul des horaires
- après ou avant le calcul automatique, l'utilisateur peut modifier l'heure manuellement en modifiant le champ heure éditable.
- sous le planning, un bouton "Envoyer" permet d'envoyer la convocation.

### 4.2 Calcul des horaires

Cas particulier PACS : les examens PACS durent longtemps.
Si un candidat passe :
- PACS_TC et (PACS_GDR ou PACS_CRISE ou PACS_HOM) : PACS_TC 09h30, suivant à 12h30
- PACS_TC et 2 parmi (PACS_GDR, PACS_CRISE, PACS_HOM) : PACS_TC à 13h30, les 2 autres à 09h30 et 11h10
- PACS_TC et 3 parmi (PACS_GDR, PACS_CRISE, PACS_HOM) : PACS_TC à 13h30, 2 autres à 09h30 et 11h10 et le 3ème à 15h40
- PACS_ARCHI toujours le matin à 09h30, les autres l'après à partir de 13h

Si parmi les candidats, plusieurs passent le même examen, on programme d'abord les examens qui sont communs à plusieurs candidats.
Exemple : si 3 candidats passent PASSI_AUDIT et 2 candidats passent PACS_GDR, on planifie les examens PASSI_AUDIT à 09h30 et les examens PACS_GDR à 09h30.
Les examens suivants sont planifiés à la suite du précédent. La durée des examens est dans la colonne "Durée (minutes)".
Si la durée des examens consécutifs durent plus de 1h30, on ajoute une pause de 10 minutes.
Exemple : Si 2 candidats passent PASSI_AUDIT et PASSI_CODE, on planifie PASSI_AUDIT à 09h30 puis PASSI_CODE à 10h10
les examens du matin ne doivent pas dépasser 12h30.
Puis on planifie à partir de 13h.

### 4.3 Génération de l'e-mail

Template par défaut (personnalisable dans power automate) :

```
destinataires :
- le surveillant du centre d'examens
- le responsable examens de l'entreprise du candidat
- le candidat

Objet : Convocation aux examens — [Programmes] du [Date_examen]

Madame, Monsieur [Prénom] [Nom],

Nous avons le plaisir de vous convoquer aux examens suivants :
  Date      : [Date_examen]
  Lieu      : [nom du centre], [adresse du centre d'examen]

Tableau des examens :
  [Qualification] : [Heure début], [Durée]

Merci de vous présenter 15 minutes avant l'heure de convocation,
muni(e) d'une pièce d'identité en cours de validité.

Cordialement,
Certi-Trust FRANCE SAS
```

### 4.4 Envoi

- si la colonne "convocation_envoyee" de tous les examens d'un candidat est vide ou que la qualification ne correspond pas ou la date_heure ne correspond pas ou que le nom du "centre" de session_examens_ecrits ne correspond pas, le bouton "envoyer" est accessible
- Le bouton "envoyer" permet d'envoyer les informations à Power automate pour émission de l'email (comme le fait déjà src\demande-devis-examens\demande_devis_widget.html et src\convocation-ecrits)
- En cas de succès :
  - dans la colonne "convocation_envoyee" de chaque examen écrit du candidat, stocker en format texte le nom de la qualification, et la date_heure (de début) et le nom du "centre" de la "sessions_examens_ecrits" de l'examen.
  - le bouton envoyer la convocation n'est plus accessible
  - si la qualification de l'examen change ou la date_heure début ou le centre change, et qu'ils ne correspondent plus à la convocation qui a été envoyée, le bouton "Envoyer" devient de nouveau accessible pour renvoyer la convocation à tous les examens du candidat de cette session.
- En cas d'erreur : affichage du message d'erreur


## 5. Contraintes techniques

Comme src\demande-devis-examens\demande_devis_widget.html

## 6. Comportement aux cas d'erreur

| Situation | Comportement attendu |
|-----------|---------------------|
| Colonne Email manquante | Message d'avertissement, envoi bloqué |
| API inaccessible | Message d'erreur, statut non modifié |
| Email invalide | Validation avant envoi, message utilisateur |
| Envoi partiel (multi) | Rapport par candidat (succès / échec) |

## 7. Critères d'acceptation

- [ ] L'e-mail de convocation est envoyé avec les données correctes du candidat sélectionné
- [ ] Le statut d'envoi est mis à jour dans Grist après chaque envoi
- [ ] Les erreurs d'envoi sont visibles et tracées
