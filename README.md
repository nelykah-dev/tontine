# 🌱 Gestionnaire de Tontine (Épargne Collective Rotative)

Application web développée avec **Django** permettant de gérer facilement des tontines (systèmes d'épargne rotative et solidaire), d'administrer les groupes, d'inscrire des membres, de planifier les tours de distribution de cagnotte et de suivre les cotisations avec détection des retards de paiement.

---

## 🚀 Fonctionnalités Principales

### 1. 👥 Gestion des Groupes de Tontine (CRUD complet)
* Création, modification, consultation détaillée et suppression de groupes.
* Définition du montant unitaire de cotisation, de la périodicité (hebdomadaire, bimensuelle, mensuelle) et du chef de groupe.
* Calcul automatique de la cagnotte totale par tour (`montantCotisation × nombre_membres`).

### 2. 👤 Gestion des Membres & Adhésions
* Ajout et modification des membres (nom, prénom, identifiant, email, contact téléphonique).
* Adhésion d'un membre à un ou plusieurs groupes de tontine.
* Prévention des doublons d'adhésion (`unique_together`).
* Retrait d'un membre d'un groupe avec confirmation.

### 3. 🎯 Tours de Versement (Cagnottes)
* Définition de l'ordre de passage des bénéficiaires.
* Programmation des dates de distribution prévues.
* Montant de la cagnotte calculé automatiquement ou personnalisable.
* Mise en évidence du **prochain bénéficiaire** sur la page de détail du groupe.
* Validation rapide des versements (« Complété » / « En attente »).

### 4. 💳 Enregistrement & Suivi des Cotisations
* Enregistrement des paiements par membre et par tour de versement.
* Suivi des statuts de versement : **Confirmé**, **En attente**, **En retard**.
* Journal global des cotisations avec filtres par statut.
* Synthèse financière : total encaissé, cotisations en attente, nombre de retards.

### 5. 🎨 Interface & Ergonomie
* Charte graphique épurée et moderne aux tons verts naturels (`#2f6b3a`, `#1f4d28`, `#f4f7f0`).
* Navigation intuitive, cartes de statistiques, tableaux clairs et badges visuels.
* Messages flash de confirmation (succès, avertissement, erreur) sur toutes les actions.
* Formulaires validés côté serveur avec retour d'erreurs explicite.

---

## 🛠️ Stack Technique

* **Framework :** Python 3.12+ / Django 6.1
* **Base de données :** SQLite (embarquée)
* **Frontend :** HTML5, CSS3 responsive sans dépendance JS lourde
* **Typographie :** Google Fonts (Poppins)

---

## 📦 Installation & Démarrage

### 1. Cloner le projet
```bash
git clone <URL_DU_DEPOT>
cd "Gestionnaire de tontine"
```

### 2. Créer et activer l'environnement virtuel
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

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Appliquer les migrations de base de données
```bash
python manage.py migrate
```

### 5. (Optionnel) Créer un compte administrateur
```bash
python manage.py createsuperuser
```

### 6. Lancer le serveur de développement
```bash
python manage.py runserver
```

Rendez-vous sur [http://127.0.0.1:8000/](http://127.0.0.1:8000/) dans votre navigateur.
L'interface d'administration Django est accessible sur [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

---

## 🧪 Exécution des Tests

Le projet inclut une suite de tests unitaires et d'intégration validant les modèles, formulaires et vues :

```bash
python manage.py test
```

---

## 📁 Structure du Projet

```text
├── db.sqlite3                # Base de données de développement (ignorée par Git)
├── manage.py                 # Script de gestion Django
├── requirements.txt          # Dépendances Python
├── .gitignore                # Fichiers et dossiers exclus de Git
├── README.md                 # Documentation du projet
├── tontine/                  # Configuration du projet Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── tontineapp/               # Application de gestion de tontine
    ├── models.py             # Modèles : Membre, TontineGroup, Membership, Tour, Cotisation
    ├── forms.py              # Formulaires avec validations
    ├── views.py              # Logique des contrôleurs et actions CRUD
    ├── urls.py               # Routes de l'application
    ├── admin.py              # Configuration avancée de l'administration
    ├── tests.py              # Tests unitaires et d'intégration
    ├── static/
    │   └── tontineapp/
    │       └── style.css     # Charte graphique verte
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

