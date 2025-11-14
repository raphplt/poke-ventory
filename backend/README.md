# Backend

API FastAPI pour Poke-ventory - Gestion d'inventaire Pokémon

## Prérequis

- Python 3.8+
- pip

## Installation

```bash
# Créer un environnement virtuel
python -m venv .venv

# Activer l'environnement virtuel
source .venv/bin/activate  # sous Windows: .venv\Scripts\activate

# Installer les dépendances
pip install fastapi uvicorn[standard]

# Sauvegarder les dépendances
pip freeze > requirements.txt
```

## Démarrage

```bash
# Activer l'environnement virtuel si ce n'est pas déjà fait
source .venv/bin/activate

# Lancer le serveur de développement
uvicorn app.main:app --reload

# Le serveur sera accessible sur http://localhost:8000
```

## Endpoints disponibles

### Health Check

- **GET** `/health`
  - Description: Vérifier l'état de l'API
  - Réponse: `{"status": "ok"}`

## Documentation interactive

Une fois le serveur lancé, vous pouvez accéder à :

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Structure du projet

```text
backend/
├── app/
│   └── main.py          # Point d'entrée de l'application
├── requirements.txt     # Dépendances Python
└── README.md           # Cette documentation
```

## Développement

### Ajouter des dépendances

```bash
pip install <package>
pip freeze > requirements.txt
```

### Variables d'environnement

Créer un fichier `.env` à la racine du dossier backend avec les variables nécessaires.

## Production

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer en production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
