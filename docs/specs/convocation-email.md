# Cahier des charges — Widget Convocation par e-mail

**Projet :** Grist Widgets — Certi-Trust FRANCE SAS  
**Widget :** `src/convocation-email/`  
**Statut :** Spécification initiale  
**Date :** 2026-06-19

---

## 1. Contexte et objectif

Les gestionnaires d'examens doivent envoyer des convocations aux candidats inscrits. Aujourd'hui cette opération est manuelle (copier-coller, envoi un par un). Ce widget permet d'envoyer des convocations directement depuis Grist, en un clic, à partir des données de la table des candidats.

## 2. Utilisateurs cibles

- Gestionnaires d'examens Certi-Trust
- Responsables de session

## 3. Données en entrée (colonnes Grist mappées)

| Colonne Grist | Rôle | Type |
|---------------|------|------|
| `Prénom` | Prénom du candidat | Texte |
| `Nom` | Nom du candidat | Texte |
| `Email` | Adresse e-mail du destinataire | Texte |
| `Examen` | Intitulé de l'examen | Texte |
| `Date_examen` | Date de l'examen | Date |
| `Heure_debut` | Heure de convocation | Texte |
| `Lieu` | Adresse ou salle d'examen | Texte |
| `Statut_convocation` | Statut d'envoi (à écrire) | Texte |

## 4. Fonctionnalités

### 4.1 Vue principale

- Affiche les informations du candidat sélectionné (ligne active dans Grist)
- Prévisualisation du corps de l'e-mail avant envoi
- Bouton **Envoyer la convocation**
- Bouton **Envoyer à tous les candidats** (mode multi-lignes)

### 4.2 Génération de l'e-mail

Template par défaut (personnalisable dans le widget) :

```
Objet : Convocation à l'examen — [Examen] du [Date_examen]

Madame, Monsieur [Prénom] [Nom],

Nous avons le plaisir de vous convoquer à l'examen :

  Examen    : [Examen]
  Date      : [Date_examen]
  Heure     : [Heure_debut]
  Lieu      : [Lieu]

Merci de vous présenter 15 minutes avant l'heure de convocation,
muni(e) d'une pièce d'identité en cours de validité.

Cordialement,
Certi-Trust FRANCE SAS
```

### 4.3 Envoi

- Appel à une API d'envoi configurable (endpoint paramétrable dans le widget)
- En cas de succès : mise à jour de `Statut_convocation` → `"Envoyé le JJ/MM/AAAA"`
- En cas d'erreur : affichage du message d'erreur, `Statut_convocation` → `"Erreur"`

### 4.4 Configuration (panneau latéral du widget)

- URL de l'API d'envoi d'e-mail
- Clé API (stockée localement dans `localStorage`)
- Nom et e-mail expéditeur

## 5. Contraintes techniques

- Fichier HTML autonome, pas de build
- Pas d'appel direct SMTP depuis le navigateur — nécessite un service intermédiaire (ex. API REST sur serveur ou service transactionnel type Brevo/Mailjet)
- L'URL de l'API est configurable pour permettre un déploiement flexible

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
- [ ] La prévisualisation correspond exactement à l'e-mail envoyé
- [ ] L'envoi groupé fonctionne pour N candidats sans blocage de l'interface
- [ ] Les erreurs d'envoi sont visibles et tracées
