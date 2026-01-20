"""
Authentication Module
Module d'authentification sécurisée
"""

from .authentication import (
    # Exceptions
    AuthenticationError,
    ValidationError,
    
    # Password management
    hash_password,
    verify_password,
    
    # Token management
    create_access_token,
    decode_access_token,
    is_token_valid,
    
    # Validation
    validate_username,
    validate_email,
    validate_password,
    validate_registration,
    
    # Session helpers
    get_current_user_from_token
)

__all__ = [
    "AuthenticationError",
    "ValidationError",
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "is_token_valid",
    "validate_username",
    "validate_email",
    "validate_password",
    "validate_registration",
    "get_current_user_from_token"
]
