"""
Database CRUD Operations
Opérations de base de données pour utilisateurs, émotions et conversations
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from .models import User, EmotionRecord, Conversation


# ==================== USER OPERATIONS ====================

def create_user(db: Session, username: str, email: str, password_hash: str) -> User:
    """Crée un nouvel utilisateur"""
    user = User(
        username=username,
        email=email,
        password_hash=password_hash
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Récupère un utilisateur par son nom d'utilisateur"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Récupère un utilisateur par son email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Récupère un utilisateur par son ID"""
    return db.query(User).filter(User.id == user_id).first()


def update_user_login(db: Session, user_id: int) -> None:
    """Met à jour la date de dernière connexion"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.last_login = datetime.utcnow()
        db.commit()


def update_user_consent(db: Session, user_id: int, consent: bool) -> None:
    """Met à jour le consentement webcam de l'utilisateur"""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.consent_webcam = consent
        db.commit()


# ==================== EMOTION OPERATIONS ====================

def add_emotion_record(
    db: Session, 
    user_id: int, 
    emotion: str, 
    confidence: float, 
    context: str = None
) -> EmotionRecord:
    """Ajoute un enregistrement d'émotion"""
    record = EmotionRecord(
        user_id=user_id,
        emotion=emotion,
        confidence=confidence,
        context=context
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_user_emotions(
    db: Session, 
    user_id: int, 
    limit: int = 100
) -> List[EmotionRecord]:
    """Récupère les dernières émotions d'un utilisateur"""
    return db.query(EmotionRecord)\
        .filter(EmotionRecord.user_id == user_id)\
        .order_by(desc(EmotionRecord.timestamp))\
        .limit(limit)\
        .all()


def get_emotions_by_period(
    db: Session, 
    user_id: int, 
    days: int = 7
) -> List[EmotionRecord]:
    """Récupère les émotions sur une période donnée"""
    start_date = datetime.utcnow() - timedelta(days=days)
    return db.query(EmotionRecord)\
        .filter(
            EmotionRecord.user_id == user_id,
            EmotionRecord.timestamp >= start_date
        )\
        .order_by(EmotionRecord.timestamp)\
        .all()


def get_emotion_statistics(db: Session, user_id: int, days: int = 7) -> Dict[str, Any]:
    """
    Calcule les statistiques émotionnelles d'un utilisateur
    Retourne la distribution des émotions et l'émotion dominante
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Compter les émotions par type
    emotion_counts = db.query(
        EmotionRecord.emotion,
        func.count(EmotionRecord.id).label('count'),
        func.avg(EmotionRecord.confidence).label('avg_confidence')
    ).filter(
        EmotionRecord.user_id == user_id,
        EmotionRecord.timestamp >= start_date
    ).group_by(EmotionRecord.emotion).all()
    
    if not emotion_counts:
        return {
            "distribution": {},
            "dominant_emotion": None,
            "total_records": 0,
            "period_days": days
        }
    
    # Calculer la distribution
    total = sum(ec.count for ec in emotion_counts)
    distribution = {
        ec.emotion: {
            "count": ec.count,
            "percentage": round((ec.count / total) * 100, 1),
            "avg_confidence": round(ec.avg_confidence, 2)
        }
        for ec in emotion_counts
    }
    
    # Trouver l'émotion dominante
    dominant = max(emotion_counts, key=lambda x: x.count)
    
    return {
        "distribution": distribution,
        "dominant_emotion": dominant.emotion,
        "total_records": total,
        "period_days": days
    }


def get_emotion_trend(db: Session, user_id: int, days: int = 7) -> List[Dict]:
    """Récupère la tendance émotionnelle par jour"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    records = db.query(EmotionRecord)\
        .filter(
            EmotionRecord.user_id == user_id,
            EmotionRecord.timestamp >= start_date
        )\
        .order_by(EmotionRecord.timestamp)\
        .all()
    
    # Grouper par jour
    daily_data = {}
    for record in records:
        day = record.timestamp.strftime("%Y-%m-%d")
        if day not in daily_data:
            daily_data[day] = {"emotions": [], "count": 0}
        daily_data[day]["emotions"].append(record.emotion)
        daily_data[day]["count"] += 1
    
    # Calculer l'émotion dominante par jour
    trend = []
    for day, data in sorted(daily_data.items()):
        emotion_counts = {}
        for emotion in data["emotions"]:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        dominant = max(emotion_counts, key=emotion_counts.get)
        trend.append({
            "date": day,
            "dominant_emotion": dominant,
            "total_detections": data["count"],
            "distribution": emotion_counts
        })
    
    return trend


# ==================== CONVERSATION OPERATIONS ====================

def add_conversation_message(
    db: Session,
    user_id: int,
    role: str,
    content: str,
    emotion_context: str = None
) -> Conversation:
    """Ajoute un message à la conversation"""
    message = Conversation(
        user_id=user_id,
        role=role,
        content=content,
        emotion_context=emotion_context
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_conversation_history(
    db: Session,
    user_id: int,
    limit: int = 50
) -> List[Conversation]:
    """Récupère l'historique de conversation d'un utilisateur"""
    return db.query(Conversation)\
        .filter(Conversation.user_id == user_id)\
        .order_by(Conversation.timestamp)\
        .limit(limit)\
        .all()


def get_recent_conversation(
    db: Session,
    user_id: int,
    hours: int = 24
) -> List[Conversation]:
    """Récupère les conversations récentes"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    return db.query(Conversation)\
        .filter(
            Conversation.user_id == user_id,
            Conversation.timestamp >= start_time
        )\
        .order_by(Conversation.timestamp)\
        .all()


def clear_conversation_history(db: Session, user_id: int) -> int:
    """Efface l'historique de conversation d'un utilisateur"""
    deleted = db.query(Conversation)\
        .filter(Conversation.user_id == user_id)\
        .delete()
    db.commit()
    return deleted


# ==================== ANALYTICS ====================

def get_user_summary(db: Session, user_id: int) -> Dict[str, Any]:
    """Récupère un résumé complet de l'activité utilisateur"""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    total_emotions = db.query(func.count(EmotionRecord.id))\
        .filter(EmotionRecord.user_id == user_id).scalar()
    
    total_messages = db.query(func.count(Conversation.id))\
        .filter(Conversation.user_id == user_id).scalar()
    
    stats_7d = get_emotion_statistics(db, user_id, days=7)
    stats_30d = get_emotion_statistics(db, user_id, days=30)
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None
        },
        "statistics": {
            "total_emotion_records": total_emotions,
            "total_messages": total_messages,
            "last_7_days": stats_7d,
            "last_30_days": stats_30d
        }
    }
