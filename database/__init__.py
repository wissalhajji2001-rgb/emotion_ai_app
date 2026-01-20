"""
Database Module
Module de gestion de base de données SQLite
"""

from .models import (
    User,
    EmotionRecord,
    Conversation,
    init_database,
    get_db,
    get_db_session,
    engine,
    SessionLocal,
    Base
)

from .crud import (
    # User operations
    create_user,
    get_user_by_username,
    get_user_by_email,
    get_user_by_id,
    update_user_login,
    update_user_consent,
    
    # Emotion operations
    add_emotion_record,
    get_user_emotions,
    get_emotions_by_period,
    get_emotion_statistics,
    get_emotion_trend,
    
    # Conversation operations
    add_conversation_message,
    get_conversation_history,
    get_recent_conversation,
    clear_conversation_history,
    
    # Analytics
    get_user_summary
)

__all__ = [
    # Models
    "User",
    "EmotionRecord", 
    "Conversation",
    "init_database",
    "get_db",
    "get_db_session",
    "engine",
    "SessionLocal",
    "Base",
    
    # CRUD
    "create_user",
    "get_user_by_username",
    "get_user_by_email",
    "get_user_by_id",
    "update_user_login",
    "update_user_consent",
    "add_emotion_record",
    "get_user_emotions",
    "get_emotions_by_period",
    "get_emotion_statistics",
    "get_emotion_trend",
    "add_conversation_message",
    "get_conversation_history",
    "get_recent_conversation",
    "clear_conversation_history",
    "get_user_summary"
]
