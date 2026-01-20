"""
Conversation Engine Module
Module de conversation IA empathique
"""

from .engine import (
    Message,
    ConversationEngine,
    get_conversation_engine,
    reset_conversation_engine,
    EMOTION_CONTEXT_FR
)

__all__ = [
    "Message",
    "ConversationEngine",
    "get_conversation_engine",
    "reset_conversation_engine",
    "EMOTION_CONTEXT_FR"
]
