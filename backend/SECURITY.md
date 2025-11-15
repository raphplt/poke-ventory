# Sécurité et Protection des Routes

## Authentification JWT

L'API utilise l'authentification JWT (JSON Web Tokens) pour sécuriser les routes.

### Types de tokens

1. **Access Token** : Valide 30 minutes, utilisé pour authentifier les requêtes
2. **Refresh Token** : Valide 7 jours, utilisé pour renouveler l'access token

## Protection des routes

### 1. Route publique (pas d'authentification)

```python
@router.get("/cards", response_model=List[CardResponse])
def get_all_cards(db: Session = Depends(get_db)):
    # Accessible sans authentification
    cards = db.query(Card).all()
    return cards
```

### 2. Route protégée (authentification requise)

```python
from app.utils.dependencies import get_current_user
from app.models.user import User

@router.post("/cards", response_model=CardResponse)
def create_card(
    card: CardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 🔒 Protection JWT
):
    # Seuls les utilisateurs authentifiés peuvent accéder
    # current_user contient l'utilisateur connecté
    return card
```

### 3. Route avec vérification des permissions

```python
@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Vérifier que l'utilisateur modifie son propre profil
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que votre propre profil"
        )

    # Logique de mise à jour...
```

### 4. Route réservée aux administrateurs (future implémentation)

```python
from app.utils.dependencies import require_admin

@router.delete("/admin/users/{user_id}")
def delete_user_admin(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)  # 🔒 Réservé aux admins
):
    # Seuls les administrateurs peuvent supprimer des utilisateurs
    user = db.query(User).filter(User.id == user_id).first()
    db.delete(user)
    db.commit()
```

## Utilisation côté client

### 1. Login et récupération du token

```typescript
const response = await fetch("/api/auth/login", {
	method: "POST",
	headers: { "Content-Type": "application/json" },
	body: JSON.stringify({
		username: "user",
		password: "password",
	}),
});

const { access_token } = await response.json();
// Stocker le token (localStorage, cookie, etc.)
localStorage.setItem("access_token", access_token);
```

### 2. Appel d'une route protégée

```typescript
const token = localStorage.getItem("access_token");

const response = await fetch("/api/cards", {
	method: "POST",
	headers: {
		"Content-Type": "application/json",
		Authorization: `Bearer ${token}`, // 🔑 Token JWT
	},
	body: JSON.stringify(cardData),
});
```

### 3. Renouvellement du token

```typescript
const refresh_token = localStorage.getItem("refresh_token");

const response = await fetch("/api/auth/refresh", {
	method: "POST",
	headers: { "Content-Type": "application/json" },
	body: JSON.stringify({ refresh_token }),
});

const { access_token } = await response.json();
localStorage.setItem("access_token", access_token);
```

## État actuel des routes

### Routes publiques

- `GET /api/cards` - Liste des cartes
- `GET /api/cards/{card_id}` - Détail d'une carte
- `GET /api/sets` - Liste des sets
- `GET /api/sets/{set_id}` - Détail d'un set
- `GET /api/series` - Liste des séries
- `GET /api/series/{series_id}` - Détail d'une série
- `POST /api/users` - Inscription (création de compte)
- `POST /api/auth/login` - Connexion
- `POST /api/auth/refresh` - Renouvellement du token

### Routes protégées (authentification requise)

- `GET /api/auth/me` - Profil utilisateur
- `GET /api/users` - Liste des utilisateurs
- `GET /api/users/{user_id}` - Détail d'un utilisateur
- `PUT /api/users/{user_id}` - Modification (uniquement son propre profil)
- `DELETE /api/users/{user_id}` - Suppression (uniquement son propre compte)
- `POST /api/cards` - Création de carte
- `PUT /api/cards/{card_id}` - Modification de carte
- `DELETE /api/cards/{card_id}` - Suppression de carte
- `POST /api/sets` - Création de set
- `PUT /api/sets/{set_id}` - Modification de set
- `DELETE /api/sets/{set_id}` - Suppression de set
- `POST /api/series` - Création de série
- `PUT /api/series/{series_id}` - Modification de série
- `DELETE /api/series/{series_id}` - Suppression de série

## Configuration

Les paramètres JWT sont configurés dans `app/utils/jwt.py` :

```python
SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # À définir dans .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

**Important** : Assurez-vous de définir `JWT_SECRET_KEY` dans votre fichier `.env` :

```bash
JWT_SECRET_KEY=votre_clé_secrète_très_longue_et_aléatoire
```

## Tests avec curl

### Route publique

```bash
curl http://localhost:8000/api/cards
```

### Route protégée (sans token → 401)

```bash
curl http://localhost:8000/api/cards -X POST
```

### Route protégée (avec token → 200)

```bash
TOKEN="votre_access_token"
curl http://localhost:8000/api/cards \
  -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id":"card1","name":"Pikachu",...}'
```

## Dépendances disponibles

### `get_current_user`

Récupère l'utilisateur actuellement connecté à partir du JWT.

### `get_current_active_user`

Vérifie que l'utilisateur est actif (nécessite un champ `is_active`).

### `require_admin`

Vérifie que l'utilisateur est administrateur (nécessite un champ `role` ou `is_admin`).

## Gestion des erreurs

### 401 Unauthorized

- Token manquant
- Token expiré
- Token invalide
- Utilisateur introuvable

### 403 Forbidden

- Permissions insuffisantes
- Tentative d'accès à une ressource d'un autre utilisateur

### 400 Bad Request

- Format de requête invalide
- Données manquantes ou incorrectes
