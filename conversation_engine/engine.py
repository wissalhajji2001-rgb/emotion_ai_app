"""
Conversation Engine Module
Agent conversationnel empathique
Supporte: Ollama (LOCAL), Groq (GRATUIT), Claude (payant), ou mode hors-ligne
"""

import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import json
import requests

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Représente un message dans la conversation"""
    role: str  # 'user' ou 'assistant'
    content: str
    emotion_context: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, str]:
        """Convertit en format API"""
        return {"role": self.role, "content": self.content}


# Traduction des émotions en français pour le contexte
EMOTION_CONTEXT_FR = {
    "happy": "heureux/heureuse",
    "sad": "triste",
    "angry": "en colère",
    "neutral": "calme",
    "surprise": "surpris(e)",
    "fear": "anxieux/anxieuse",
    "disgust": "dégoûté(e)"
}


class ConversationEngine:
    """
    Moteur de conversation empathique
    Priorité: Ollama (local) > Groq (gratuit) > Claude (payant)
    """
    
    # Prompt système pour l'assistant empathique
    SYSTEM_PROMPT = """Tu es un assistant IA empathique et bienveillant nommé "Émoji" 🤗.
    
Ton rôle est d'accompagner l'utilisateur en fonction de son état émotionnel détecté par webcam.

## Tes caractéristiques :
- Tu parles en français de façon naturelle et chaleureuse
- Tu es attentif aux émotions et tu adaptes ton ton
- Tu poses des questions ouvertes pour encourager l'expression
- Tu donnes des conseils bienveillants sans être moralisateur
- Tu peux faire de l'humour léger pour détendre l'atmosphère
- Tu encourages positivement sans être condescendant

## Adaptation selon les émotions :
- 😊 HEUREUX : Partage la joie, renforce la positivité, célèbre les moments
- 😢 TRISTE : Écoute active, empathie profonde, soutien doux, suggère des activités réconfortantes
- 😠 EN COLÈRE : Calme et apaisant, reconnais la frustration, propose des exercices de respiration
- 😐 NEUTRE : Engage la conversation, pose des questions intéressantes
- 😲 SURPRIS : Curiosité, explore ce qui a causé la surprise
- 😨 PEUR : Rassurant, présence stable, techniques de relaxation
- 🤢 DÉGOÛT : Compréhension, change de sujet si nécessaire

## Format de tes réponses :
- Réponses concises (2-4 phrases généralement)
- Utilise des emojis avec modération
- Pose UNE question ouverte à la fin quand c'est approprié
- Ne répète pas "Je vois que tu es [émotion]" à chaque message

## Exemples de réponses :
- "Ça fait plaisir de te voir sourire ! 😊 Qu'est-ce qui te met de bonne humeur aujourd'hui ?"
- "Je sens que quelque chose te tracasse... Je suis là si tu veux en parler. 💙"
- "Prends une grande inspiration... voilà, doucement. Qu'est-ce qui t'a frustré ?"

Sois authentique, chaleureux et aide l'utilisateur à se sentir écouté et compris."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le moteur de conversation
        Détecte automatiquement quelle API utiliser
        Priorité: Ollama (local) > Groq (gratuit) > Claude (payant)
        """
        # Configuration Ollama (local)
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
        
        # Configuration Groq (gratuit)
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Configuration Claude (payant)
        self.anthropic_api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        self.client = None
        self.api_type = None  # 'ollama', 'groq', 'anthropic', ou None
        self.conversation_history: List[Message] = []
        self.current_emotion: Optional[str] = None
        self.emotion_history: List[str] = []
        
        self._initialize_client()
    
    def _check_ollama_available(self) -> bool:
        """Vérifie si Ollama est disponible localement"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _initialize_client(self):
        """Initialise le client API (Ollama prioritaire car local et gratuit)"""
        
        # 1. Essayer Ollama d'abord (LOCAL et GRATUIT)
        if self._check_ollama_available():
            self.api_type = 'ollama'
            logger.info(f"✅ Ollama détecté ! Modèle: {self.ollama_model} (LOCAL)")
            return
        
        # 2. Essayer Groq ensuite (GRATUIT en ligne)
        if self.groq_api_key and self.groq_api_key != "your-groq-api-key-here":
            try:
                from groq import Groq
                self.client = Groq(api_key=self.groq_api_key)
                self.api_type = 'groq'
                logger.info("✅ Client Groq API initialisé (GRATUIT)")
                return
            except ImportError:
                logger.warning("⚠️ Module groq non installé. Tapez: pip install groq")
            except Exception as e:
                logger.error(f"❌ Erreur Groq: {e}")
        
        # 3. Essayer Claude ensuite (payant)
        if self.anthropic_api_key and self.anthropic_api_key != "your-anthropic-api-key-here":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                self.api_type = 'anthropic'
                logger.info("✅ Client Claude API initialisé")
                return
            except ImportError:
                logger.warning("⚠️ Module anthropic non installé")
            except Exception as e:
                logger.error(f"❌ Erreur Claude API: {e}")
        
        # Mode hors-ligne
        logger.warning("⚠️ Aucune API configurée. Mode hors-ligne activé.")
        logger.info("💡 Options: 1) Installez Ollama, 2) Ajoutez GROQ_API_KEY dans .env")
        self.api_type = None
    
    def set_emotion_context(self, emotion: str, confidence: float = 0.0):
        """
        Met à jour le contexte émotionnel
        
        Args:
            emotion: Émotion détectée (en anglais)
            confidence: Score de confiance
        """
        self.current_emotion = emotion
        self.emotion_history.append(emotion)
        
        # Garder seulement les 10 dernières émotions
        if len(self.emotion_history) > 10:
            self.emotion_history.pop(0)
    
    def _get_emotion_context_message(self) -> str:
        """Génère le contexte émotionnel pour le prompt"""
        if not self.current_emotion:
            return ""
        
        emotion_fr = EMOTION_CONTEXT_FR.get(self.current_emotion, self.current_emotion)
        
        # Analyser la tendance émotionnelle
        trend_info = ""
        if len(self.emotion_history) >= 3:
            recent = self.emotion_history[-3:]
            if all(e == self.current_emotion for e in recent):
                trend_info = f" Cette émotion semble persistante."
        
        return f"[Contexte émotionnel: L'utilisateur semble {emotion_fr}.{trend_info}]"
    
    def generate_response(
        self, 
        user_message: str,
        emotion: Optional[str] = None,
        emotion_confidence: float = 0.0
    ) -> str:
        """
        Génère une réponse empathique basée sur le message et l'émotion
        
        Args:
            user_message: Message de l'utilisateur
            emotion: Émotion actuelle détectée
            emotion_confidence: Confiance de la détection
            
        Returns:
            Réponse de l'assistant
        """
        # Mettre à jour le contexte émotionnel
        if emotion:
            self.set_emotion_context(emotion, emotion_confidence)
        
        # Ajouter le message utilisateur à l'historique
        self.conversation_history.append(Message(
            role="user",
            content=user_message,
            emotion_context=emotion
        ))
        
        # Générer la réponse selon l'API disponible
        if self.api_type == 'ollama':
            response = self._call_ollama_api(user_message)
        elif self.client and self.api_type == 'groq':
            response = self._call_groq_api(user_message)
        elif self.client and self.api_type == 'anthropic':
            response = self._call_claude_api(user_message)
        else:
            response = self._generate_fallback_response(user_message)
        
        # Ajouter la réponse à l'historique
        self.conversation_history.append(Message(
            role="assistant",
            content=response,
            emotion_context=emotion
        ))
        
        return response
    
    def _call_ollama_api(self, user_message: str) -> str:
        """Appelle l'API Ollama (LOCAL) pour générer une réponse"""
        try:
            # Construire le contexte émotionnel
            emotion_context = self._get_emotion_context_message()
            
            # Préparer les messages pour l'API
            messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
            
            # Ajouter l'historique récent
            for i, msg in enumerate(self.conversation_history[-10:]):
                content = msg.content
                if i == len(self.conversation_history[-10:]) - 1 and emotion_context:
                    content = f"{emotion_context}\n\n{content}"
                messages.append({"role": msg.role, "content": content})
            
            # Appel API Ollama
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.ollama_model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 500
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", self._generate_fallback_response(user_message))
            else:
                logger.error(f"Erreur Ollama: {response.status_code}")
                return self._generate_fallback_response(user_message)
            
        except Exception as e:
            logger.error(f"Erreur API Ollama: {e}")
            return self._generate_fallback_response(user_message)
    
    def _call_groq_api(self, user_message: str) -> str:
        """Appelle l'API Groq (GRATUIT) pour générer une réponse"""
        try:
            # Construire le contexte émotionnel
            emotion_context = self._get_emotion_context_message()
            
            # Préparer les messages pour l'API
            messages = []
            
            # Ajouter l'historique récent
            for i, msg in enumerate(self.conversation_history[-10:]):
                content = msg.content
                if i == len(self.conversation_history[-10:]) - 1 and emotion_context:
                    content = f"{emotion_context}\n\n{content}"
                messages.append({"role": msg.role, "content": content})
            
            # Appel API Groq
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Modèle gratuit et performant
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    *messages
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Erreur API Groq: {e}")
            return self._generate_fallback_response(user_message)
    
    def _call_claude_api(self, user_message: str) -> str:
        """Appelle l'API Claude pour générer une réponse"""
        try:
            # Construire le contexte émotionnel
            emotion_context = self._get_emotion_context_message()
            
            # Préparer les messages pour l'API
            messages = []
            
            # Ajouter le contexte émotionnel au premier message si présent
            for i, msg in enumerate(self.conversation_history[-10:]):  # Limiter l'historique
                content = msg.content
                if i == len(self.conversation_history[-10:]) - 1 and emotion_context:
                    # Ajouter le contexte au dernier message utilisateur
                    content = f"{emotion_context}\n\n{content}"
                messages.append({"role": msg.role, "content": content})
            
            # Appel API
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                system=self.SYSTEM_PROMPT,
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Erreur API Claude: {e}")
            return self._generate_fallback_response(user_message)
    
    def _generate_fallback_response(self, user_message: str) -> str:
        """
        Génère une réponse de secours si l'API n'est pas disponible
        Réponses pré-définies basées sur l'émotion
        """
        emotion = self.current_emotion or "neutral"
        
        responses = {
            "happy": [
                "Ça fait plaisir de te voir de bonne humeur ! 😊 Qu'est-ce qui te rend si joyeux aujourd'hui ?",
                "Ton sourire est contagieux ! Continue comme ça ! Raconte-moi ta journée ?",
                "Super ! J'adore cette énergie positive ! Qu'est-ce qui s'est passé de bien ?"
            ],
            "sad": [
                "Je vois que tu traverses un moment difficile... Je suis là pour toi. 💙 Tu veux en parler ?",
                "C'est ok de ne pas aller bien parfois. Qu'est-ce qui te tracasse ?",
                "Je suis là pour t'écouter, sans jugement. Prends ton temps pour me dire ce qui ne va pas."
            ],
            "angry": [
                "Je comprends que tu sois frustré(e). Prends une grande respiration... 🌬️ Qu'est-ce qui s'est passé ?",
                "La colère, c'est normal. Veux-tu en parler pour te libérer un peu ?",
                "Je t'écoute. Parfois, exprimer ce qui nous énerve fait du bien."
            ],
            "neutral": [
                "Hey ! Comment vas-tu ? Qu'est-ce qui t'amène aujourd'hui ? 👋",
                "Coucou ! Je suis content de te voir. De quoi voudrais-tu parler ?",
                "Salut ! Comment se passe ta journée jusqu'ici ?"
            ],
            "fear": [
                "Je suis là, tout va bien se passer. 🤗 Qu'est-ce qui t'inquiète ?",
                "Respire doucement... Je comprends que tu puisses te sentir anxieux. Parle-moi.",
                "Tu n'es pas seul(e). Dis-moi ce qui te fait peur, on peut en discuter ensemble."
            ],
            "surprise": [
                "Oh ! Tu as l'air surpris(e) ! Il s'est passé quelque chose d'inattendu ?",
                "Wow, je vois la surprise sur ton visage ! Raconte-moi !",
                "Qu'est-ce qui t'a surpris comme ça ? Je suis curieux !"
            ],
            "disgust": [
                "Hmm, quelque chose ne semble pas te plaire... Tu veux en parler ?",
                "Je vois que quelque chose te dérange. Qu'est-ce qui s'est passé ?",
                "On dirait que tu as vécu quelque chose de désagréable. Je t'écoute."
            ]
        }
        
        import random
        emotion_responses = responses.get(emotion, responses["neutral"])
        return random.choice(emotion_responses)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Retourne l'historique de conversation formaté"""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "emotion": msg.emotion_context,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
            }
            for msg in self.conversation_history
        ]
    
    def clear_history(self):
        """Efface l'historique de conversation"""
        self.conversation_history.clear()
        self.emotion_history.clear()
        self.current_emotion = None
    
    def get_greeting(self, emotion: Optional[str] = None) -> str:
        """
        Génère un message d'accueil personnalisé
        
        Args:
            emotion: Émotion initiale détectée
            
        Returns:
            Message d'accueil
        """
        if emotion:
            self.set_emotion_context(emotion)
        
        greetings = {
            "happy": "Hey ! 😊 Je vois que tu es de bonne humeur ! Ça fait plaisir !",
            "sad": "Bonjour... 💙 Je suis là si tu as besoin de parler.",
            "angry": "Salut. Je vois que quelque chose te tracasse. Je t'écoute.",
            "neutral": "Bonjour ! 👋 Comment puis-je t'aider aujourd'hui ?",
            "fear": "Coucou... 🤗 Je suis là, tout va bien. De quoi voudrais-tu parler ?",
            "surprise": "Oh ! Bonjour ! Tu as l'air surpris(e) de me voir ! 😄",
            "disgust": "Salut... Quelque chose ne va pas ? Je suis là pour en parler."
        }
        
        return greetings.get(emotion or "neutral", greetings["neutral"])
    
    def generate_wellness_tip(self, emotion: str) -> str:
        """
        Génère un conseil bien-être basé sur l'émotion
        
        Args:
            emotion: Émotion actuelle
            
        Returns:
            Conseil bien-être
        """
        tips = {
            "happy": [
                "💡 Astuce : Note ce moment de bonheur dans un journal pour t'en souvenir !",
                "💡 Partage ta bonne humeur avec quelqu'un, la joie est contagieuse !",
                "💡 Profite de cette énergie pour faire quelque chose que tu aimes !"
            ],
            "sad": [
                "💡 Astuce : Une petite promenade à l'air frais peut aider à éclaircir les idées.",
                "💡 Écoute une musique que tu aimes, ça peut aider à remonter le moral.",
                "💡 Prends un moment pour toi : un thé chaud, une couverture, et du repos."
            ],
            "angry": [
                "💡 Astuce : Essaie la respiration 4-7-8 : inspire 4s, retiens 7s, expire 8s.",
                "💡 L'exercice physique aide à évacuer la frustration. Une petite marche ?",
                "💡 Écris ce qui t'énerve sur un papier, puis froisse-le et jette-le !"
            ],
            "neutral": [
                "💡 C'est le moment parfait pour essayer quelque chose de nouveau !",
                "💡 Profite de ce calme pour planifier quelque chose qui te fait envie.",
                "💡 Un bon moment pour pratiquer la gratitude : 3 choses positives du jour ?"
            ],
            "fear": [
                "💡 Astuce : Ancre-toi dans le présent - nomme 5 choses que tu vois autour de toi.",
                "💡 La respiration profonde active le système parasympathique et calme l'anxiété.",
                "💡 Rappelle-toi : 90% de nos inquiétudes ne se réalisent jamais."
            ]
        }
        
        import random
        emotion_tips = tips.get(emotion, tips["neutral"])
        return random.choice(emotion_tips)


# Instance globale pour utilisation simplifiée
_engine_instance: Optional[ConversationEngine] = None


def get_conversation_engine(api_key: Optional[str] = None) -> ConversationEngine:
    """Retourne l'instance singleton du moteur de conversation"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = ConversationEngine(api_key)
    return _engine_instance


def reset_conversation_engine():
    """Réinitialise l'instance du moteur de conversation"""
    global _engine_instance
    if _engine_instance:
        _engine_instance.clear_history()
    _engine_instance = None
