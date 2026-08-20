# Cahier des charges — Widget Demande d'un devis examens

**Projet :** Grist Widgets — Certi-Trust FRANCE SAS  
**Widget :** `src/cr-oral/`  
**Statut :** Spécification initiale  
**Date :** 2026-07-20

---

## 1. Contexte et objectif

Après chaque oral, un CR est envoyé au candidat, les examinateurs et le responsable examens du client en copie carbone.

Actuellement, un pdf généré par docs\specs\TEM-420_CR_evaluation_Oral_PACS_V5_publipostage.docx en publipostage puis le pdf est joint à un email.
Pour le publipostage, on créer un csv grace à la colonne Compte_rendu_csv qui contient toutes les informations.

Il faut désormais envoyer un html dans le corps de texte de l'email via power automate depuis l'adresse examens@certi-trust.com

## 2. Utilisateurs cibles

- évaluateurs

## 3. Modèle de données Grist

### Table principale

Examens_oraux

## 4. Fonctionnalités

### 4.1 Interface principale

Un widget doit être ajouté à la page "CR Oraux" de docs\specs\Evaluations(45).grist
sur ce widget apparaissent l'email du candidat, les emails en copie carbone : responsable examens de l'entreprise et les deux examinateurs.
L'objet est "CR d'oral [Programme]"
Le corps du texte de l'email, tel qu'il apparaîtra dans l'email, déjà formaté html, sur le modèle de docs\specs\TEM-420_CR_evaluation_Oral_PACS_V5_publipostage.docx.

### 4.5 Actions

- Convertir les données de la ligne correspondant à l'examen oral en CR d'oral au format html sur le modèle de docs\specs\TEM-420_CR_evaluation_Oral_PACS_V5_publipostage.docx
- Permettre à l'utilisateur de corriger les données dans la fiche EXAMENS_ORAUX de la page "CR oraux"
- Un bouton "Envoyer le CR" permet d'envoyer les informations à Power automate pour émission de l'email (comme le fait déjà src\demande-devis-examens\demande_devis_widget.html)
- Après envoi, marquer la colonne "CR_envoye" à true (colonne que je vais créer)

## 5. Contraintes techniques

TODO

## 6. Comportement aux cas d'erreur

- Alerter s'il manque une information : s'il manque une note (nombre de notes < nombre de qualifications), s'il manque un examinateur (il en faut deux), en cas d'anomalie

## 7. Critères d'acceptation

à rédiger par Claude.
