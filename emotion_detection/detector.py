"""
Emotion Detection Module
Détection des émotions faciales en temps réel
Version légère sans TensorFlow/PyTorch
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging
import random

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Emotion(Enum):
    """Énumération des émotions détectables"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    NEUTRAL = "neutral"
    SURPRISE = "surprise"
    FEAR = "fear"
    DISGUST = "disgust"


# Traduction des émotions en français
EMOTION_TRANSLATIONS = {
    "happy": "😊 Heureux",
    "sad": "😢 Triste",
    "angry": "😠 En colère",
    "neutral": "😐 Neutre",
    "surprise": "😲 Surpris",
    "fear": "😨 Peur",
    "disgust": "🤢 Dégoût"
}

# Couleurs pour l'affichage (BGR)
EMOTION_COLORS = {
    "happy": (0, 255, 0),      # Vert
    "sad": (255, 0, 0),        # Bleu
    "angry": (0, 0, 255),      # Rouge
    "neutral": (128, 128, 128), # Gris
    "surprise": (0, 255, 255),  # Jaune
    "fear": (255, 0, 255),     # Magenta
    "disgust": (0, 128, 0)     # Vert foncé
}


@dataclass
class EmotionResult:
    """Résultat de détection d'émotion"""
    emotion: str
    confidence: float
    all_emotions: Dict[str, float]
    face_box: Optional[Tuple[int, int, int, int]] = None
    
    @property
    def emotion_french(self) -> str:
        """Retourne l'émotion en français avec emoji"""
        return EMOTION_TRANSLATIONS.get(self.emotion, self.emotion)
    
    @property
    def confidence_percent(self) -> str:
        """Retourne la confiance en pourcentage"""
        return f"{self.confidence * 100:.1f}%"


class EmotionDetector:
    """
    Classe principale de détection des émotions
    Utilise FER (Facial Emotion Recognition) basé sur un CNN
    """
    
    def __init__(self):
        """Initialise le détecteur d'émotions (version légère OpenCV)"""
        self.face_cascade = None
        self.smile_cascade = None
        self.eye_cascade = None
        self.emotion_buffer = []
        self.buffer_size = 5
        self._initialized = False
        self._initialize()
    
    def _initialize(self):
        """Initialisation du détecteur avec OpenCV uniquement"""
        try:
            # Charger les cascade classifiers pour la détection de visage et sourire
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            smile_cascade_path = cv2.data.haarcascades + 'haarcascade_smile.xml'
            eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            self.smile_cascade = cv2.CascadeClassifier(smile_cascade_path)
            self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
            
            # Historique pour stabiliser les détections
            self.emotion_buffer = []
            self.buffer_size = 5
            
            self._initialized = True
            logger.info("✅ Détecteur d'émotions initialisé (mode OpenCV)")
        except Exception as e:
            logger.error(f"❌ Erreur d'initialisation: {e}")
            self._initialized = False
    
    def detect_emotion(self, frame: np.ndarray) -> Optional[EmotionResult]:
        """
        Détecte l'émotion dominante dans une frame
        Utilise des heuristiques basées sur OpenCV (sourires, yeux)
        
        Args:
            frame: Image BGR (format OpenCV)
            
        Returns:
            EmotionResult ou None si aucun visage détecté
        """
        if frame is None or frame.size == 0:
            return None
        
        try:
            return self._detect_with_opencv(frame)
        except Exception as e:
            logger.error(f"Erreur de détection: {e}")
            return None
    
    def _detect_with_opencv(self, frame: np.ndarray) -> Optional[EmotionResult]:
        """
        Détection basée sur OpenCV avec heuristiques
        Analyse les caractéristiques faciales pour estimer l'émotion
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Détecter les visages
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5,
            minSize=(60, 60)
        )
        
        if len(faces) == 0:
            return None
        
        # Prendre le plus grand visage
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        face_roi = gray[y:y+h, x:x+w]
        
        # Analyser les caractéristiques faciales
        emotion_scores = self._analyze_facial_features(face_roi, gray, x, y, w, h)
        
        # Trouver l'émotion dominante
        dominant_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = emotion_scores[dominant_emotion]
        
        # Stabiliser avec le buffer
        self.emotion_buffer.append(dominant_emotion)
        if len(self.emotion_buffer) > self.buffer_size:
            self.emotion_buffer.pop(0)
        
        # Utiliser l'émotion la plus fréquente dans le buffer
        if len(self.emotion_buffer) >= 3:
            from collections import Counter
            emotion_counts = Counter(self.emotion_buffer)
            dominant_emotion = emotion_counts.most_common(1)[0][0]
        
        return EmotionResult(
            emotion=dominant_emotion,
            confidence=confidence,
            all_emotions=emotion_scores,
            face_box=(x, y, w, h)
        )
    
    def _analyze_facial_features(
        self, 
        face_roi: np.ndarray,
        gray: np.ndarray,
        x: int, y: int, w: int, h: int
    ) -> Dict[str, float]:
        """
        Analyse les caractéristiques faciales pour estimer les émotions
        Utilise la détection de sourires et d'yeux comme indicateurs
        """
        # Initialiser les scores
        scores = {
            "happy": 0.15,
            "sad": 0.15,
            "angry": 0.15,
            "neutral": 0.25,
            "surprise": 0.10,
            "fear": 0.10,
            "disgust": 0.10
        }
        
        # Détecter les sourires
        smiles = self.smile_cascade.detectMultiScale(
            face_roi,
            scaleFactor=1.5,
            minNeighbors=15,
            minSize=(25, 25)
        )
        
        # Détecter les yeux
        eyes = self.eye_cascade.detectMultiScale(
            face_roi,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(20, 20)
        )
        
        # Si sourire détecté → plus de chances d'être heureux
        if len(smiles) > 0:
            scores["happy"] = 0.70 + random.uniform(0, 0.15)
            scores["neutral"] = 0.10
            scores["sad"] = 0.05
        
        # Analyser l'ouverture des yeux
        if len(eyes) >= 2:
            # Yeux bien ouverts
            eye_areas = [ew * eh for (ex, ey, ew, eh) in eyes]
            avg_eye_area = sum(eye_areas) / len(eye_areas)
            
            # Grands yeux = surprise possible
            if avg_eye_area > (w * h * 0.02):
                scores["surprise"] = max(scores["surprise"], 0.40 + random.uniform(0, 0.1))
        elif len(eyes) < 2 and len(smiles) == 0:
            # Yeux fermés ou froncés sans sourire
            scores["angry"] = max(scores["angry"], 0.35 + random.uniform(0, 0.1))
            scores["sad"] = max(scores["sad"], 0.30 + random.uniform(0, 0.1))
        
        # Si aucune caractéristique particulière → neutre
        if len(smiles) == 0 and len(eyes) >= 2:
            scores["neutral"] = max(scores["neutral"], 0.50 + random.uniform(0, 0.15))
        
        # Normaliser les scores
        total = sum(scores.values())
        scores = {k: round(v / total, 2) for k, v in scores.items()}
        
        return scores
    
    def draw_emotion_overlay(
        self, 
        frame: np.ndarray, 
        result: EmotionResult
    ) -> np.ndarray:
        """
        Dessine l'overlay avec l'émotion détectée sur la frame
        
        Args:
            frame: Image BGR
            result: Résultat de la détection
            
        Returns:
            Image avec overlay
        """
        if result is None:
            return frame
        
        output = frame.copy()
        
        # Dessiner le rectangle autour du visage
        if result.face_box:
            x, y, w, h = result.face_box
            color = EMOTION_COLORS.get(result.emotion, (255, 255, 255))
            cv2.rectangle(output, (x, y), (x + w, y + h), color, 2)
            
            # Afficher l'émotion au-dessus du rectangle
            label = f"{result.emotion_french} ({result.confidence_percent})"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            thickness = 2
            
            # Calculer la taille du texte
            (text_width, text_height), baseline = cv2.getTextSize(
                label, font, font_scale, thickness
            )
            
            # Fond pour le texte
            cv2.rectangle(
                output,
                (x, y - text_height - 10),
                (x + text_width + 10, y),
                color,
                -1
            )
            
            # Texte
            cv2.putText(
                output,
                label,
                (x + 5, y - 5),
                font,
                font_scale,
                (255, 255, 255),
                thickness
            )
        
        return output
    
    def get_emotion_bar_data(self, result: EmotionResult) -> List[Dict[str, Any]]:
        """
        Prépare les données pour un graphique en barres des émotions
        
        Args:
            result: Résultat de la détection
            
        Returns:
            Liste de dictionnaires pour le graphique
        """
        if result is None:
            return []
        
        return [
            {
                "emotion": EMOTION_TRANSLATIONS.get(emotion, emotion),
                "score": score,
                "percentage": f"{score * 100:.1f}%"
            }
            for emotion, score in sorted(
                result.all_emotions.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
        ]


class EmotionAnalyzer:
    """
    Analyseur d'émotions pour la logique décisionnelle
    Détecte les patterns émotionnels et adapte les réponses
    """
    
    def __init__(self, history_size: int = 10):
        """
        Args:
            history_size: Nombre d'émotions à garder en mémoire
        """
        self.history: List[EmotionResult] = []
        self.history_size = history_size
    
    def add_emotion(self, result: EmotionResult):
        """Ajoute une émotion à l'historique"""
        if result:
            self.history.append(result)
            if len(self.history) > self.history_size:
                self.history.pop(0)
    
    def get_dominant_emotion(self) -> Optional[str]:
        """Retourne l'émotion dominante récente"""
        if not self.history:
            return None
        
        emotion_counts = {}
        for result in self.history:
            emotion = result.emotion
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        return max(emotion_counts, key=emotion_counts.get)
    
    def is_emotion_persistent(self, emotion: str, threshold: float = 0.6) -> bool:
        """
        Vérifie si une émotion est persistante
        
        Args:
            emotion: Émotion à vérifier
            threshold: Seuil de persistance (0-1)
            
        Returns:
            True si l'émotion est persistante
        """
        if not self.history:
            return False
        
        count = sum(1 for r in self.history if r.emotion == emotion)
        return (count / len(self.history)) >= threshold
    
    def get_emotional_trend(self) -> str:
        """
        Analyse la tendance émotionnelle
        
        Returns:
            'improving', 'stable', ou 'declining'
        """
        if len(self.history) < 3:
            return "stable"
        
        # Score de positivité pour chaque émotion
        positivity_scores = {
            "happy": 1.0,
            "surprise": 0.5,
            "neutral": 0.0,
            "fear": -0.5,
            "sad": -0.7,
            "disgust": -0.8,
            "angry": -1.0
        }
        
        # Calculer les scores moyens pour la première et la dernière moitié
        mid = len(self.history) // 2
        first_half = self.history[:mid]
        second_half = self.history[mid:]
        
        avg_first = np.mean([
            positivity_scores.get(r.emotion, 0) for r in first_half
        ])
        avg_second = np.mean([
            positivity_scores.get(r.emotion, 0) for r in second_half
        ])
        
        diff = avg_second - avg_first
        
        if diff > 0.2:
            return "improving"
        elif diff < -0.2:
            return "declining"
        else:
            return "stable"
    
    def get_response_suggestions(self) -> Dict[str, Any]:
        """
        Génère des suggestions de réponse basées sur l'état émotionnel
        
        Returns:
            Dictionnaire avec les suggestions d'adaptation
        """
        dominant = self.get_dominant_emotion()
        trend = self.get_emotional_trend()
        
        suggestions = {
            "dominant_emotion": dominant,
            "trend": trend,
            "tone": "neutral",
            "approach": [],
            "avoid": []
        }
        
        if dominant == "sad":
            suggestions["tone"] = "empathique et réconfortant"
            suggestions["approach"] = [
                "Poser des questions ouvertes sur les sentiments",
                "Offrir du soutien sans juger",
                "Suggérer des activités positives"
            ]
            suggestions["avoid"] = [
                "Minimiser les sentiments",
                "Être trop enthousiaste"
            ]
            
            if self.is_emotion_persistent("sad"):
                suggestions["approach"].append(
                    "Suggérer délicatement de parler à quelqu'un de confiance"
                )
        
        elif dominant == "angry":
            suggestions["tone"] = "calme et apaisant"
            suggestions["approach"] = [
                "Reconnaître la frustration",
                "Proposer des exercices de respiration",
                "Rediriger vers des solutions"
            ]
            suggestions["avoid"] = [
                "Être confrontationnel",
                "Ignorer la colère"
            ]
        
        elif dominant == "happy":
            suggestions["tone"] = "joyeux et énergique"
            suggestions["approach"] = [
                "Renforcer la positivité",
                "Partager l'enthousiasme",
                "Encourager à maintenir cette énergie"
            ]
            suggestions["avoid"] = [
                "Être rabat-joie"
            ]
        
        elif dominant == "fear":
            suggestions["tone"] = "rassurant et calme"
            suggestions["approach"] = [
                "Rassurer sur la situation",
                "Proposer des techniques de relaxation",
                "Être une présence stable"
            ]
            suggestions["avoid"] = [
                "Amplifier les inquiétudes"
            ]
        
        else:  # neutral or other
            suggestions["tone"] = "amical et engageant"
            suggestions["approach"] = [
                "Engager la conversation naturellement",
                "Poser des questions pour mieux comprendre"
            ]
        
        # Ajuster selon la tendance
        if trend == "declining":
            suggestions["approach"].append(
                "Porter une attention particulière au bien-être"
            )
        elif trend == "improving":
            suggestions["approach"].append(
                "Encourager la progression positive"
            )
        
        return suggestions
    
    def clear_history(self):
        """Efface l'historique des émotions"""
        self.history.clear()


# Singleton pour utilisation globale
_detector_instance: Optional[EmotionDetector] = None


def get_emotion_detector() -> EmotionDetector:
    """Retourne l'instance singleton du détecteur"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = EmotionDetector()
    return _detector_instance
