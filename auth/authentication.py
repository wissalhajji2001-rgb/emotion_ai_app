"""
Authentication Module
Gestion sécurisée de l'authentification avec bcrypt et JWT
"""

import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import re

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production-123!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


class AuthenticationError(Exception):
    """Exception personnalisée pour les erreurs d'authentification"""
    pass


class ValidationError(Exception):
    """Exception pour les erreurs de validation"""
    pass


# ==================== PASSWORD MANAGEMENT ====================

def hash_password(password: str) -> str:
    """
    Hash un mot de passe avec bcrypt
    Args:
        password: Mot de passe en clair
    Returns:
        Hash du mot de passe
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Vérifie si un mot de passe correspond au hash
    Args:
        password: Mot de passe en clair
        hashed_password: Hash stocké
    Returns:
        True si correspondance, False sinon
    """
    try:
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


# ==================== TOKEN MANAGEMENT ====================

def create_access_token(user_id: int, username: str) -> str:
    """
    Crée un token JWT pour l'utilisateur
    Args:
        user_id: ID de l'utilisateur
        username: Nom d'utilisateur
    Returns:
        Token JWT
    """
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Décode et vérifie un token JWT
    Args:
        token: Token JWT
    Returns:
        Payload du token ou None si invalide
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token expiré. Veuillez vous reconnecter.")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Token invalide.")


def is_token_valid(token: str) -> bool:
    """Vérifie si un token est valide"""
    try:
        decode_access_token(token)
        return True
    except AuthenticationError:
        return False


# ==================== VALIDATION ====================

def validate_username(username: str) -> bool:
    """
    Valide le format du nom d'utilisateur
    - 3 à 20 caractères
    - Lettres, chiffres, underscores
    """
    if not username or len(username) < 3 or len(username) > 20:
        raise ValidationError("Le nom d'utilisateur doit contenir entre 3 et 20 caractères.")
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError("Le nom d'utilisateur ne peut contenir que des lettres, chiffres et underscores.")
    
    return True


def validate_email(email: str) -> bool:
    """Valide le format de l'email"""
    if not email:
        raise ValidationError("L'email est requis.")
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError("Format d'email invalide.")
    
    return True


def validate_password(password: str) -> bool:
    """
    Valide la force du mot de passe
    - Minimum 8 caractères
    - Au moins une majuscule
    - Au moins une minuscule
    - Au moins un chiffre
    """
    if not password or len(password) < 8:
        raise ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Le mot de passe doit contenir au moins une majuscule.")
    
    if not re.search(r'[a-z]', password):
        raise ValidationError("Le mot de passe doit contenir au moins une minuscule.")
    
    if not re.search(r'\d', password):
        raise ValidationError("Le mot de passe doit contenir au moins un chiffre.")
    
    return True


def validate_registration(username: str, email: str, password: str, confirm_password: str) -> bool:
    """Valide toutes les données d'inscription"""
    validate_username(username)
    validate_email(email)
    validate_password(password)
    
    if password != confirm_password:
        raise ValidationError("Les mots de passe ne correspondent pas.")
    
    return True


# ==================== SESSION HELPERS ====================

def get_current_user_from_token(token: str) -> Dict[str, Any]:
    """
    Récupère les informations utilisateur depuis le token
    Args:
        token: Token JWT
    Returns:
        Dictionnaire avec user_id et username
    """
    payload = decode_access_token(token)
    if not payload:
        raise AuthenticationError("Impossible de récupérer l'utilisateur.")
    
    return {
        "user_id": payload.get("user_id"),
        "username": payload.get("username")
    }
