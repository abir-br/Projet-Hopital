# Projet Hôpital — Application de Gestion Hospitalière

Application web de gestion hospitalière développée avec **Flask** et **SQLite**, permettant à différents profils de personnel (médecins, infirmiers) de se connecter et de gérer patients, soins, séjours, réunions et services.

---

## Structure du projet

```
Projet-Hopital/
├── bdd/
│   └── hopital.db                 
    └── Login_v1/
        ├── app.py                 
        ├── requirements.txt        
        ├── setup.bat               
        ├── database.db             
        ├── votre_base_de_donnees.db
        ├── static/
        │   ├── css/                
        │   ├── js/                 
        │   ├── images/             
        │   ├── fonts/             
        │   └── vendor/             
        └── templates/
            ├── index.html          
            ├── medecin/
            │   ├── medecin.html
            │   ├── patients.html
            │   ├── services.html
            │   └── reunions.html
            └── infirmier/
                ├── infirmier.html
                ├── patients.html
                ├── soins.html
                └── reunions.html
```

---

## Description des fonctionnalités

### Authentification (`app.py` — route `/`)
Connexion unique par email/mot de passe, avec redirection automatique selon le type d'utilisateur (`medecin` ou `infirmier`), via la table `personnel`.

### Espace Médecin
| Route                          | Description                                                          |
|---------------------------------|-----------------------------------------------------------------------|
| `/medecin`                      | Tableau de bord médecin                                               |
| `/patients`                     | Liste des patients suivis (ou non encore visités) par le médecin      |
| `/ajouter_patient`              | Ajout d'un nouveau patient                                             |
| `/modifier_patient`             | Modification des informations d'un patient                            |
| `/get_patient/<id>`             | Récupération des informations d'un patient (JSON)                     |
| `/supprimer_patient/<id>`       | Suppression d'un patient et de ses dépendances (visites, soins, séjours) |
| `/visites/patient/<id>`         | Historique des visites médicales d'un patient (JSON)                  |
| `/api/soins/<id>`               | Soins associés à un patient (JSON)                                     |
| `/api/sejours/<id>`             | Séjours (chambre/lit) d'un patient (JSON)                              |
| `/api/medicaments/<id>`         | Médicaments prescrits à un patient (JSON)                              |
| `/reunions`                     | Réunions du médecin connecté, avec participants                       |
| `/services` *(services.html)*   | Services, médecins/infirmiers/patients rattachés                      |

### Espace Infirmier
| Route                            | Description                                                    |
|-----------------------------------|-----------------------------------------------------------------|
| `/infirmier`                      | Tableau de bord infirmier, liste des soins assignés             |
| `/infirmier/soins`                | Détail des soins avec médicaments associés                      |
| `/infirmier/reunions`             | Réunions liées aux soins de l'infirmier                          |
| `/infirmier/patients`             | Patients suivis par l'infirmier connecté                         |
| `/infirmier/patient/<id>/soins`   | Historique des soins d'un patient pour cet infirmier (JSON)      |

### Réunions
| Route                              | Description                                     |
|--------------------------------------|--------------------------------------------------|
| `/reunion/<id>/participants`        | Liste des participants d'une réunion (JSON)      |

---

## Base de données (`bdd/hopital.db`)

Schéma relationnel articulé autour des entités suivantes :

| Table                  | Rôle                                                       |
|-------------------------|--------------------------------------------------------------|
| `personnel`             | Table commune (nom, prénom, type, email, login, mot de passe) |
| `medecin` / `infirmier` / `admin` / `nettoyeur` | Sous-types de personnel, rattachés à un `service` |
| `service`                | Services hospitaliers (référent médecin, admin responsable)  |
| `chambre` / `lit`        | Chambres et lits, rattachés à un service                     |
| `patient`                | Informations administratives et médicales du patient         |
| `visite_medicale`        | Visites d'un médecin auprès d'un patient                      |
| `soin`                   | Soins prodigués par un infirmier à un patient                |
| `medicament` / `medicament_soin` | Médicaments et leur association à un soin (quantité) |
| `sejour`                 | Séjour d'un patient (lit, dates d'arrivée/sortie)             |
| `reunion` / `participants_reunion` | Réunions et leurs participants                      |
| `nettoyage_chambre`      | Suivi du nettoyage des chambres                               |

---

## Installation

```bash
cd "page login/Login_v1"

# Créer et activer un environnement virtuel
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS

# Installer les dépendances
pip install -r requirements.txt
```

Dépendances principales : `Flask==3.1.0`, `Jinja2==3.1.6`, `Werkzeug==3.1.3`, `MarkupSafe==3.0.2`, `click==8.1.8`, `itsdangerous==2.2.0`, `blinker==1.9.0`, `colorama==0.4.6`, `tabulate==0.9.0`.

## Exécution

```bash
# Windows : lance automatiquement l'environnement virtuel et l'application
setup.bat

# Ou manuellement
python app.py
```

