# Tableau de bord Achats (Purchase Dashboard)

Module Odoo 18 — Dashboard Achats dynamique avec KPI en temps reel, filtres interactifs et configuration par societe.

**Auteur :** SOPROMER  
**Version :** 18.0.2.0.0  
**Licence :** LGPL-3  
**Dependance :** `purchase`

---

## Fonctionnalites

### KPI en temps reel (8 indicateurs)

| Indicateur | Description |
|---|---|
| **Demandes de prix** | Nombre de commandes en etat brouillon (draft) |
| **Envoyees** | Demandes de prix envoyees au fournisseur |
| **A approuver** | Commandes en attente d'approbation |
| **Confirmees** | Commandes d'achat confirmees |
| **Verrouillees** | Commandes terminee et verrouillees |
| **Annulees** | Commandes annulees |
| **En retard** | Commandes confirmees dont la date de reception prevue est depassee avec reception incomplete |
| **Depenses ce mois** | Montant total des commandes confirmees du mois en cours |

Chaque carte KPI est **cliquable** et ouvre la liste filtree des commandes correspondantes.

### Graphique des achats

- Graphique en barres du montant des achats par jour (commandes confirmees par date d'approbation)
- Periode configurable : **7, 14 ou 30 jours**
- Resume en haut a droite : total commandes et montant sur la periode stats

### Tableau des commandes actives

- Liste des commandes non terminees (brouillon, envoyee, a approuver, confirmee)
- Colonnes : Reference, Fournisseur, Montant, Etat, Reception
- Statut de reception : Complet, Partiel, En attente, N/A
- Cliquer sur une ligne ouvre le formulaire de la commande
- Nombre d'enregistrements configurable (par defaut : 50)

### Top 10 Fournisseurs

- Classement des 10 fournisseurs avec le plus gros volume d'achats confirmes
- Colonnes : Rang, Fournisseur, Nombre de commandes, Montant total
- Periode basee sur le filtre "Periode stats" (par defaut : 30 jours)
- Cliquer sur un fournisseur ouvre la liste de ses commandes confirmees

---

## Filtres dynamiques

Le panneau de filtres s'ouvre via le bouton **Filtres** dans l'en-tete du dashboard.

| Filtre | Description |
|---|---|
| **Date debut** | Filtrer les commandes a partir de cette date |
| **Date fin** | Filtrer les commandes jusqu'a cette date |
| **Acheteur** | Filtrer par responsable d'achat (liste dynamique) |
| **Fournisseur** | Filtrer par fournisseur (liste dynamique, jusqu'a 200) |
| **Jours graphique** | Nombre de jours affiches dans le graphique (7/14/30) |
| **Periode stats** | Periode pour les statistiques recentes (7/30/60/90 jours) |

- Un **point bleu** apparait sur le bouton Filtres quand des filtres sont actifs
- Bouton **Appliquer** pour lancer la recherche
- Bouton **Reinitialiser** pour revenir aux valeurs par defaut

---

## Rafraichissement automatique

Le selecteur dans l'en-tete permet de configurer le rafraichissement automatique :

- **Off** — rafraichissement manuel uniquement
- **30 secondes**
- **1 minute**
- **2 minutes**
- **5 minutes**

L'heure de la derniere mise a jour est affichee a cote des controles.

---

## Installation

### Prerequis

- Odoo 18 Community ou Enterprise
- Module `purchase` (Achats) installe et configure

### Etapes

1. Copier le dossier `purchase_dashboard` dans le repertoire des addons personnalises :

   ```
   cp -r purchase_dashboard /chemin/vers/odoo18/custom-addons/
   ```

2. Mettre a jour la liste des modules dans Odoo :

   **Applications > Mettre a jour la liste des applications**

3. Rechercher et installer le module :

   **Applications > Rechercher "Tableau de bord Achats" > Installer**

4. Ou via la ligne de commande :

   ```bash
   python odoo-bin -d ma_base -u purchase_dashboard --stop-after-init
   ```

### Mise a jour

Pour mettre a jour apres modification :

```bash
python odoo-bin -d ma_base -u purchase_dashboard --stop-after-init
```

---

## Configuration

### Acceder a la configuration

**Achats > Configuration > Config. Dashboard**

> Seuls les **Responsables Dashboard Achat** (groupe `purchase_dashboard.group_purchase_dashboard_manager`) ou les **Responsables des achats** Odoo (`purchase.group_purchase_manager`) peuvent modifier la configuration.

### Parametres disponibles

| Parametre | Par defaut | Description |
|---|---|---|
| Jours graphique achats | 7 | Nombre de jours dans le graphique en barres |
| Jours statistiques recentes | 30 | Periode pour le calcul des totaux et du top fournisseurs |
| Limite commandes actives | 50 | Nombre max de commandes affichees dans le tableau |
| Rafraichissement auto | Desactive | Intervalle de mise a jour automatique |
| Societe | Societe courante | Configuration par societe (multi-societe) |

### Multi-societe

Chaque societe peut avoir sa propre configuration. Le dashboard charge automatiquement la configuration de la societe active de l'utilisateur.

---

## Droits d'acces

### Groupes dedies

Le module cree deux groupes dans la categorie **Dashboard Achat** :

| Groupe | Voir le dashboard | Voir la config | Modifier la config |
|---|---|---|---|
| Utilisateur Dashboard Achat | Oui | Oui (lecture) | Non |
| Responsable Dashboard Achat | Oui | Oui | Oui |

### Heritage automatique

- Le groupe **Responsable Dashboard Achat** herite automatiquement du groupe **Utilisateur Dashboard Achat**
- Le groupe Odoo standard **Responsable des achats** (`purchase.group_purchase_manager`) herite automatiquement du groupe **Responsable Dashboard Achat**, ce qui lui donne un acces complet au dashboard et a sa configuration

### Resume

| Role Odoo | Acces dashboard |
|---|---|
| Utilisateur achats standard | Aucun (sauf si le groupe Dashboard est ajoute manuellement) |
| Utilisateur Dashboard Achat | Consultation du dashboard et lecture de la config |
| Responsable Dashboard Achat | Acces complet (dashboard + config en ecriture) |
| Responsable des achats (Odoo) | Acces complet (herite de Responsable Dashboard Achat) |

---

## Architecture technique

```
purchase_dashboard/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── main.py                        # Endpoints RPC
├── models/
│   ├── __init__.py
│   └── purchase_dashboard_config.py   # Modele de configuration
├── security/
│   ├── ir.model.access.csv            # Droits d'acces
│   └── purchase_dashboard_groups.xml  # Groupes de securite
├── static/src/
│   ├── css/purchase_dashboard.css     # Styles
│   ├── js/purchase_dashboard.js       # Composant OWL
│   └── xml/purchase_dashboard.xml     # Template OWL
├── views/
│   ├── purchase_dashboard_views.xml        # Menu + Action client
│   └── purchase_dashboard_config_views.xml # Vues configuration
├── doc/
│   └── guide_utilisation.md           # Guide detaille
└── README.md
```

### Endpoints API

| Route | Type | Description |
|---|---|---|
| `/purchase_dashboard/data` | JSON (POST) | Donnees du dashboard avec filtres |
| `/purchase_dashboard/filters_data` | JSON (POST) | Listes pour les selecteurs de filtres (acheteurs, fournisseurs) |

### Parametres de `/purchase_dashboard/data`

```json
{
  "filters": {
    "chart_days": 7,
    "recent_days": 30,
    "active_order_limit": 50,
    "date_from": "2026-01-01",
    "date_to": "2026-03-31",
    "responsible_id": 2,
    "partner_id": 15
  }
}
```

### Reponse de `/purchase_dashboard/data`

```json
{
  "state_counts": {
    "draft": 12,
    "sent": 5,
    "to approve": 3,
    "purchase": 28,
    "done": 15,
    "cancel": 2
  },
  "late_count": 4,
  "month_total": 125000.50,
  "daily_purchases": [
    {"date": "28/03", "amount": 15000.00, "count": 3}
  ],
  "active_orders": [],
  "recent_total_count": 28,
  "recent_total_amount": 350000.00,
  "top_suppliers": [
    {"id": 1, "name": "Fournisseur ABC", "amount": 85000.00, "count": 8}
  ],
  "config": {}
}
```

### Reponse de `/purchase_dashboard/filters_data`

```json
{
  "responsibles": [
    {"id": 2, "name": "Ahmed B."}
  ],
  "partners": [
    {"id": 15, "name": "Fournisseur XYZ"}
  ]
}
```

### Technologies

- **Frontend :** OWL 2 (framework reactif Odoo), Bootstrap 5
- **Backend :** Odoo 18 HTTP Controllers, ORM
- **Modeles interroges :** `purchase.order`, `purchase.dashboard.config`

---

## Depannage

| Probleme | Solution |
|---|---|
| Le dashboard ne s'affiche pas | Verifier que le module `purchase` est installe. Vider le cache navigateur (Ctrl+Maj+Suppr). |
| Erreur "Acces non autorise au dashboard achat" | Verifier que l'utilisateur a le groupe "Utilisateur Dashboard Achat" au minimum. |
| Le menu "Tableau de bord" n'apparait pas | Le menu est visible uniquement pour le groupe `purchase_dashboard.group_purchase_dashboard_user`. Ajouter le groupe a l'utilisateur. |
| Les filtres acheteur/fournisseur sont vides | Normal si aucune commande d'achat n'existe encore dans le systeme. |
| L'auto-refresh ne fonctionne pas | Verifier que la valeur est differente de "Off" dans le selecteur. |
| Les donnees ne correspondent pas | Cliquer sur "Actualiser" pour forcer un rechargement. |
| "Depenses ce mois" affiche 0 | Ce KPI ne compte que les commandes confirmees (state=purchase) approuvees dans le mois en cours. |
| Le top fournisseurs est vide | Aucune commande confirmee sur la periode stats selectionnee. |

---

## Licence

Ce module est distribue sous licence [LGPL-3](https://www.gnu.org/licenses/lgpl-3.0.html).
