# Backend

API FastAPI pour Poke-ventory - Gestion d'inventaire Pokémon

## Prérequis

- Python 3.8+
- pip

## Installation

### Avec `make` (recommandé, macOS & Windows)

Depuis le dossier `backend/` :

```bash
make install
```

Cette commande :

- crée un environnement virtuel `.venv` (Windows ou macOS/Linux) ;
- installe `fastapi` et `uvicorn[standard]` ;
- génère `requirements.txt`.

### Installation manuelle

macOS / Linux :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi "uvicorn[standard]"
pip freeze > requirements.txt
```

Windows (PowerShell) :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install fastapi "uvicorn[standard]"
pip freeze > requirements.txt
```

## Démarrage

### Avec `make` (recommandé)

Depuis le dossier `backend/` :

```bash
make run
```

### Démarrage manuel

macOS / Linux :

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

Windows (PowerShell) :

```powershell
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Le serveur sera accessible sur <http://localhost:8000>.

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
