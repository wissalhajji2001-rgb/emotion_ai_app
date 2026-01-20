"""
Emotion Detection Module
Module de détection d'émotions faciales
"""

from .detector import (
    Emotion,
    EmotionResult,
    EmotionDetector,
    EmotionAnalyzer,
    get_emotion_detector,
    EMOTION_TRANSLATIONS,
    EMOTION_COLORS
)

__all__ = [
    "Emotion",
    "EmotionResult",
    "EmotionDetector",
    "EmotionAnalyzer",
    "get_emotion_detector",
    "EMOTION_TRANSLATIONS",
    "EMOTION_COLORS"
]
