# Guide d'utilisation — Tableau de bord Achats

## Table des matieres

1. [Acceder au dashboard](#1-accéder-au-dashboard)
2. [Comprendre les KPI](#2-comprendre-les-kpi)
3. [Utiliser les filtres](#3-utiliser-les-filtres)
4. [Configurer le rafraichissement automatique](#4-configurer-le-rafraîchissement-automatique)
5. [Naviguer vers les commandes](#5-naviguer-vers-les-commandes)
6. [Lire le graphique des achats](#6-lire-le-graphique-des-achats)
7. [Top 10 Fournisseurs](#7-top-10-fournisseurs)
8. [Configurer les parametres par defaut](#8-configurer-les-paramètres-par-défaut)
9. [Controle d'acces](#9-contrôle-daccès)
10. [Cas d'usage courants](#10-cas-dusage-courants)

---

## 1. Acceder au dashboard

1. Ouvrir le menu principal **Achats**
2. Cliquer sur **Tableau de bord** (premier element du menu, sequence 1)

Le dashboard se charge et affiche les donnees en temps reel.

> **Note :** Le menu n'est visible que pour les utilisateurs ayant le groupe "Utilisateur Dashboard Achat" ou un groupe superieur.

---

## 2. Comprendre les KPI

Les 8 cartes en haut du dashboard affichent les compteurs principaux :

### Cartes d'etat des commandes

- **Demandes de prix** (gris/draft) — Commandes en brouillon, pas encore envoyees au fournisseur. Ce sont les demandes de prix en cours de preparation.
- **Envoyees** (sent) — Demandes de prix envoyees au fournisseur, en attente de reponse.
- **A approuver** (to approve) — Commandes qui necessitent une validation par un responsable avant confirmation.
- **Confirmees** (purchase) — Commandes d'achat validees et envoyees. La commande est ferme.
- **Verrouillees** (done) — Commandes entierement traitees et verrouillees. Aucune modification possible.
- **Annulees** (cancel) — Commandes annulees.

### Cartes d'alerte

- **En retard** (rouge) — Commandes confirmees ayant au moins une ligne dont la date de reception prevue (`date_planned`) est depassee et dont la quantite recue est inferieure a la quantite commandee. Ce sont les urgences a traiter en priorite avec les fournisseurs.
- **Depenses ce mois** — Montant total (en DH) des commandes confirmees dont la date d'approbation (`date_approve`) tombe dans le mois en cours. Cet indicateur donne une vision du budget achats consomme ce mois.

### Interaction

Cliquer sur n'importe quelle carte d'etat ouvre la **liste filtree** des commandes correspondantes dans une vue standard Odoo, ou vous pouvez trier, exporter, ou ouvrir chaque commande.

Cliquer sur **En retard** ouvre la liste des commandes confirmees (le filtrage precis des lignes en retard se fait ensuite manuellement).

---

## 3. Utiliser les filtres

### Ouvrir le panneau

Cliquer sur le bouton **Filtres** dans l'en-tete du dashboard. Un panneau apparait avec les options suivantes :

### Filtres disponibles

#### Date debut / Date fin
- Permet de restreindre les donnees a une **periode precise**
- Filtre sur la date de commande (`date_order`) des bons de commande
- Affecte les compteurs d'etat et le tableau des commandes actives
- Exemple : voir uniquement les commandes de mars 2026

#### Acheteur
- Liste deroulante contenant tous les utilisateurs ayant des commandes assignees
- Permet de voir le dashboard **du point de vue d'un acheteur specifique**
- "-- Tous --" affiche les donnees de tous les acheteurs

#### Fournisseur
- Liste deroulante des fournisseurs (jusqu'a 200 fournisseurs)
- Permet de suivre les achats aupres d'un **fournisseur specifique**
- "-- Tous --" affiche tous les fournisseurs

#### Jours graphique
- **7 jours** — vue courte, ideale pour le suivi quotidien
- **14 jours** — vue bi-hebdomadaire
- **30 jours** — vue mensuelle

#### Periode stats
- Determine la periode pour le calcul affiche en haut du graphique ("30j: X cmd / Y DH") et pour le classement Top 10 Fournisseurs
- **7 jours** — cette semaine
- **30 jours** — ce mois (par defaut)
- **60 jours** — 2 mois
- **90 jours** — trimestre

### Appliquer les filtres

1. Configurer les filtres souhaites
2. Cliquer sur **Appliquer**
3. Le dashboard se recharge avec les donnees filtrees
4. Un **point bleu** apparait sur le bouton Filtres pour indiquer que des filtres sont actifs

### Reinitialiser

Cliquer sur **Reinitialiser** pour revenir aux valeurs par defaut (7 jours graphique, 30 jours stats, aucun filtre de date/acheteur/fournisseur) et recharger toutes les donnees.

---

## 4. Configurer le rafraichissement automatique

### Depuis le dashboard

Le selecteur **Auto** dans l'en-tete permet de choisir l'intervalle :

| Option | Usage recommande |
|---|---|
| **Off** | Travail ponctuel, consultation rapide |
| **30 secondes** | Suivi en temps reel sur ecran dedie |
| **1 minute** | Supervision active des achats |
| **2 minutes** | Suivi regulier |
| **5 minutes** | Affichage permanent sur ecran mural |

### Depuis la configuration

Le responsable Dashboard Achat peut definir l'intervalle par defaut dans la configuration (voir section 8).

### Rafraichissement manuel

Le bouton **Actualiser** (icone de rafraichissement) force un rechargement immediat a tout moment.

L'heure de la derniere mise a jour est affichee a gauche des controles.

---

## 5. Naviguer vers les commandes

### Depuis les cartes KPI

Cliquer sur une carte → ouvre la **vue liste** des commandes filtrees par cet etat.

Exemples :
- Cliquer sur **Demandes de prix** → affiche toutes les commandes en brouillon
- Cliquer sur **A approuver** → affiche les commandes en attente de validation
- Cliquer sur **En retard** → affiche les commandes confirmees (filtrage supplementaire a faire manuellement)

### Depuis le tableau des commandes actives

Cliquer sur une **ligne du tableau** → ouvre le **formulaire** de la commande directement.

Les colonnes du tableau :
- **Reference** — numero de la commande (ex: PO0042)
- **Fournisseur** — nom du partenaire
- **Montant** — montant total de la commande
- **Etat** — badge colore (Brouillon, Envoyee, A approuver, Confirmee)
- **Reception** — statut de reception (Complet, Partiel, En attente, N/A)

### Depuis le Top 10 Fournisseurs

Cliquer sur une **ligne du classement** → ouvre la liste des commandes confirmees de ce fournisseur.

---

## 6. Lire le graphique des achats

### Les barres

- Chaque barre represente un jour
- La hauteur indique le **montant total des achats confirmes** ce jour-la (base sur `date_approve`)
- La valeur exacte est affichee au-dessus de chaque barre (en DH)
- La date est affichee en dessous (format jj/mm)

### Le resume

En haut a droite du graphique :
- **X cmd** — nombre total de commandes confirmees sur la periode stats
- **Y DH** — montant total des achats sur la periode stats

### Interpreter

- Des barres regulieres indiquent un rythme d'achat stable
- Des barres a zero signalent des jours sans confirmation de commande (weekend, jours feries, etc.)
- Un pic important peut signaler une grosse commande a verifier
- Une tendance a la hausse peut indiquer une augmentation des besoins en approvisionnement

---

## 7. Top 10 Fournisseurs

La section "Top 10 Fournisseurs" affiche le classement des fournisseurs par montant d'achats confirmes sur la periode stats :

| Colonne | Description |
|---|---|
| **#** | Rang du fournisseur (1 a 10) |
| **Fournisseur** | Nom du partenaire |
| **Commandes** | Nombre de commandes confirmees |
| **Montant total** | Somme des montants (en DH) |

### Interaction

Cliquer sur une ligne ouvre la **liste des commandes confirmees** de ce fournisseur dans une vue standard Odoo.

### Periode

Le classement est calcule sur la periode definie par le filtre **Periode stats** (par defaut 30 jours). Pour voir le top fournisseurs sur un trimestre, selectionnez 90 jours dans les filtres.

---

## 8. Configurer les parametres par defaut

> Reserve aux **Responsables Dashboard Achat** ou aux **Responsables des achats** Odoo

### Acceder a la configuration

**Achats > Configuration > Config. Dashboard**

### Creer une configuration

1. Cliquer sur **Nouveau**
2. Remplir les parametres :
   - **Jours graphique achats** — nombre de jours par defaut dans le graphique (defaut : 7)
   - **Jours statistiques recentes** — periode de calcul des totaux et du top fournisseurs (defaut : 30)
   - **Limite commandes actives** — combien de commandes afficher dans le tableau (defaut : 50)
   - **Rafraichissement auto** — intervalle par defaut (Desactive, 30s, 1min, 2min, 5min)
   - **Societe** — la societe concernee (en multi-societe)
3. Cliquer sur **Enregistrer**

### Multi-societe

Si vous gerez plusieurs societes, creez une configuration distincte pour chacune. Le dashboard chargera automatiquement la configuration correspondant a la societe active de l'utilisateur.

### Pas de configuration ?

Si aucune configuration n'existe pour la societe, le dashboard utilise les valeurs par defaut :
- 7 jours pour le graphique
- 30 jours pour les stats et le top fournisseurs
- 50 commandes actives max
- Pas d'auto-refresh

---

## 9. Controle d'acces

### Groupes de securite

Le module cree deux groupes dedies dans la categorie **Dashboard Achat** :

| Groupe | Dashboard | Config (lecture) | Config (ecriture) |
|---|---|---|---|
| Utilisateur Dashboard Achat | Oui | Oui | Non |
| Responsable Dashboard Achat | Oui | Oui | Oui |

### Heritage automatique

- **Responsable Dashboard Achat** herite de **Utilisateur Dashboard Achat** (pas besoin d'assigner les deux)
- Le groupe Odoo standard **Responsable des achats** (`purchase.group_purchase_manager`) herite automatiquement de **Responsable Dashboard Achat**

### En pratique

- Un **utilisateur achats standard** n'a pas acces au dashboard par defaut. Il faut lui ajouter manuellement le groupe "Utilisateur Dashboard Achat" via les parametres utilisateur.
- Un **responsable des achats** Odoo a automatiquement acces complet au dashboard et a sa configuration, sans action supplementaire.
- Les endpoints API (`/purchase_dashboard/data` et `/purchase_dashboard/filters_data`) verifient le groupe et renvoient une erreur **403 Forbidden** si l'utilisateur n'a pas les droits.

---

## 10. Cas d'usage courants

### Reunion achats hebdomadaire

1. Ouvrir le dashboard
2. Verifier la carte **En retard** en priorite — contacter les fournisseurs concernes
3. Verifier la carte **A approuver** — valider ou rejeter les commandes en attente
4. Consulter le graphique pour voir l'evolution des achats de la semaine
5. Parcourir le Top 10 Fournisseurs pour identifier les partenaires principaux

### Suivi acheteur

1. Ouvrir les filtres
2. Selectionner l'acheteur dans la liste deroulante
3. Appliquer
4. Le dashboard affiche uniquement les KPI et commandes assignes a cet acheteur
5. Utile pour les revues de performance individuelles

### Analyse fournisseur

1. Ouvrir les filtres
2. Selectionner le fournisseur dans la liste deroulante
3. Etendre la periode stats a **90 jours** pour une vue trimestrielle
4. Cliquer sur **Appliquer**
5. Le dashboard affiche uniquement les donnees de ce fournisseur
6. Consulter le graphique pour voir la regularite des commandes
7. Verifier les commandes en retard liees a ce fournisseur

### Analyse mensuelle

1. Ouvrir les filtres
2. Definir **Date debut** = 01/03/2026, **Date fin** = 31/03/2026
3. Mettre **Jours graphique** a 30
4. Mettre **Periode stats** a 30 jours
5. Appliquer
6. Le dashboard affiche la vue complete du mois de mars
7. La carte **Depenses ce mois** donne le total du mois en cours (independamment des filtres de date)

### Suivi en temps reel sur ecran dedie

1. Ouvrir le dashboard sur un ecran dedie (salle de reunion, bureau achats)
2. Configurer l'auto-refresh a **30 secondes** ou **1 minute**
3. Le dashboard se met a jour en continu sans intervention
4. Les cartes KPI et le tableau des commandes refletent l'etat en temps reel

---

## Raccourcis clavier

Le dashboard utilise les interactions souris standard d'Odoo :
- **Clic** sur une carte KPI → liste filtree des commandes
- **Clic** sur une ligne du tableau des commandes actives → formulaire de la commande
- **Clic** sur une ligne du Top 10 Fournisseurs → liste des commandes du fournisseur
- **F5** ou bouton Actualiser → rafraichir les donnees
