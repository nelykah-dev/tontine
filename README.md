# Gestionnaire de Tontine (Épargne Collective Rotative)

Application web développée avec Django pour l'administration et le suivi d'un système d'épargne collective rotative (tontine). Elle permet de gérer des groupes, d'inscrire des membres, de planifier les tours d'attribution des cagnottes et de contrôler l'état des cotisations périodiques.

---

## Fonctionnalités

### 1. Gestion des Groupes de Tontine (CRUD)
* Création, consultation détaillée, modification et suppression de groupes.
* Définition des paramètres financiers : montant unitaire de la cotisation, périodicité (hebdomadaire, bimensuelle, mensuelle) et désignation du chef de groupe.
* Calcul automatisé du montant global de la cagnotte par tour (montant de la cotisation multiplié par l'effectif du groupe).

### 2. Gestion des Membres et Adhésions
* Enregistrement et mise à jour des fiches membres (nom, prénom, identifiant, adresse courriel, contact téléphonique).
* Gestion des adhésions aux groupes avec contrôle d'intégrité (prévention des doublons par contrainte d'unicité).
* Procédure de retrait d'un membre avec demande de confirmation.

### 3. Gestion des Tours de Versement
* Définition de l'ordre d'attribution de la cagnotte entre les membres du groupe.
* Planification des échéances prévues.
* Identification du prochain bénéficiaire sur le tableau de bord du groupe.
* Clôture et validation des versements avec mise à jour du statut (En attente, Complété).

### 4. Suivi et Contrôle des Cotisations
* Enregistrement des paiements par membre et par tour de versement.
* Suivi des états de règlement : Confirmé, En attente, En retard.
* Journal centralisé des cotisations avec filtrage par statut de paiement.
* Indicateurs synthétiques : cumul des versements validés, nombre de cotisations en attente et retards constatés.

### 5. Interface Utilisateur
* Interface ergonomique structurée autour d'une charte graphique sobre.
* Tableaux de bord synthétiques avec métriques de trésorerie.
* Système de notifications pour la confirmation des opérations et la gestion des erreurs de validation des formulaires.

---

## Environnement Technique

* **Langage :** Python 3.12+
* **Framework :** Django 6.1
* **Base de données :** SQLite
* **Frontend :** HTML5, CSS3 standardisé
* **Typographie :** Polices système et Poppins

---

## Installation et Démarrage

### 1. Cloner le dépôt
```bash
git clone https://github.com/nelykah-dev/tontine.git
cd tontine
```

### 2. Création et activation de l'environnement virtuel

* **Sous Windows (PowerShell) :**
  ```powershell
  python -m venv env
  .\env\Scripts\Activate.ps1
  ```

* **Sous Linux / macOS :**
  ```bash
  python3 -m venv env
  source env/bin/activate
  ```

### 3. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 4. Application des migrations
```bash
python manage.py migrate
```

### 5. Création d'un compte administrateur (facultatif)
```bash
python manage.py createsuperuser
```

### 6. Lancement du serveur d'exécution
```bash
python manage.py runserver
```

L'application est accessible à l'adresse suivante : [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
Le module d'administration Django est disponible sur : [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## Tests Automatisés

Le projet comprend une suite de tests unitaires et d'intégration validant les modèles, les formulaires et les contrôleurs :

```bash
python manage.py test
```

---

## Arborescence du Projet

```text
├── db.sqlite3                # Base de données locale (exclue du suivi de version)
├── manage.py                 # Utilitaire d'administration Django
├── requirements.txt          # Liste des dépendances logicielles
├── .gitignore                # Règles d'exclusion Git
├── README.md                 # Documentation technique
├── tontine/                  # Module de configuration globale
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── tontineapp/               # Application métier
    ├── models.py             # Modèles : Membre, TontineGroup, Membership, Tour, Cotisation
    ├── forms.py              # Formulaires et règles de validation
    ├── views.py              # Vues et logique applicative
    ├── urls.py               # Définition des routes
    ├── admin.py              # Configuration de l'interface d'administration
    ├── tests.py              # Suite de tests automatisés
    ├── static/
    │   └── tontineapp/
    │       └── style.css     # Feuilles de style
    └── templates/
        └── tontineapp/
            ├── base.html
            ├── index.html
            ├── liste_groupes.html
            ├── detail_groupe.html
            ├── form_groupe.html
            ├── liste_membres.html
            ├── form_membre.html
            ├── form_adhesion.html
            ├── form_tour.html
            ├── form_cotisation.html
            ├── liste_cotisations.html
            └── confirmer_suppression.html
```
