"""
Database Models - SQLite with SQLAlchemy
Modèles de base de données pour l'application IA émotionnelle
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Base de données SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///emotion_ai.db")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """
    Modèle Utilisateur
    Stocke les informations d'authentification et de profil
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    consent_webcam = Column(Boolean, default=False)  # Consentement webcam (éthique IA)
    
    # Relations
    emotions = relationship("EmotionRecord", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class EmotionRecord(Base):
    """
    Historique des émotions détectées
    Stocke chaque détection avec score de confiance
    """
    __tablename__ = "emotion_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    emotion = Column(String(20), nullable=False)  # happy, sad, angry, neutral, etc.
    confidence = Column(Float, nullable=False)  # Score de confiance 0-1
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    context = Column(Text, nullable=True)  # Contexte de la conversation
    
    # Relations
    user = relationship("User", back_populates="emotions")
    
    def __repr__(self):
        return f"<EmotionRecord(emotion='{self.emotion}', confidence={self.confidence:.2f})>"


class Conversation(Base):
    """
    Historique des conversations IA
    Stocke les échanges avec l'assistant
    """
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' ou 'assistant'
    content = Column(Text, nullable=False)
    emotion_context = Column(String(20), nullable=True)  # Émotion au moment du message
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relations
    user = relationship("User", back_populates="conversations")
    
    def __repr__(self):
        return f"<Conversation(role='{self.role}', timestamp='{self.timestamp}')>"


def init_database():
    """Initialise la base de données et crée les tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Base de données initialisée avec succès!")


def get_db():
    """Générateur de session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """Retourne une nouvelle session de base de données"""
    return SessionLocal()


if __name__ == "__main__":
    init_database()
