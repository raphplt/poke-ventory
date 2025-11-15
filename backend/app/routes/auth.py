from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, Token, RefreshRequest
from app.schemas.user import UserResponse
from app.utils.security import verify_password
from app.utils.jwt import create_access_token, create_refresh_token, verify_token

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

security = HTTPBearer()


@router.post("/login", response_model=Token)
def login(
    credentials: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Authentification par username/password
    Retourne un access token et un refresh token
    """
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer les tokens
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Stocker le refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Token)
def refresh_access_token(
    refresh_request: RefreshRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Renouveler l'access token avec un refresh token
    """
    # Vérifier le refresh token
    payload = verify_token(refresh_request.refresh_token, token_type="refresh")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide ou expiré"
        )
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable"
        )
    
    # Créer un nouveau access token
    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 60 * 60
    )
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@router.post("/logout")
def logout(response: Response):
    """
    Déconnexion : supprime le refresh token du cookie
    """
    response.delete_cookie(key="refresh_token")
    return {"message": "Déconnexion réussie"}


# Dépendance pour récupérer l'utilisateur courant
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    
    # Vérifier le token
    payload = verify_token(token, token_type="access")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable"
        )
    
    return user


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Récupérer les infos de l'utilisateur connecté
    Route protégée par JWT
    """
    return current_user
