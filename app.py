"""
Emotion AI Application - Main Streamlit Interface
Application principale avec authentification, détection d'émotions et chat IA
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import time
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import (
    init_database, get_db_session,
    create_user, get_user_by_username, get_user_by_email,
    update_user_login, update_user_consent,
    add_emotion_record, get_user_emotions, get_emotion_statistics, get_emotion_trend,
    add_conversation_message, get_conversation_history, clear_conversation_history
)
from auth import (
    hash_password, verify_password, create_access_token,
    validate_registration, ValidationError
)
from emotion_detection import (
    EmotionDetector, EmotionAnalyzer, 
    EMOTION_TRANSLATIONS, EMOTION_COLORS
)
from conversation_engine import ConversationEngine

# ==================== CONFIGURATION ====================

st.set_page_config(
    page_title="🎭 Emotion AI - Assistant Émotionnel",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialiser la base de données
init_database()

# ==================== STYLES CSS ====================

st.markdown("""
<style>
    /* Style général */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Cards */
    .emotion-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    
    .stat-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    /* Chat */
    .chat-message {
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 80%;
    }
    
    .user-message {
        background: #E3F2FD;
        margin-left: auto;
        text-align: right;
    }
    
    .assistant-message {
        background: #F5F5F5;
        margin-right: auto;
    }
    
    /* Boutons */
    .stButton > button {
        border-radius: 20px;
        padding: 10px 25px;
        font-weight: 500;
    }
    
    /* Sidebar */
    .sidebar-info {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================

def init_session_state():
    """Initialise les variables de session"""
    defaults = {
        'authenticated': False,
        'user_id': None,
        'username': None,
        'token': None,
        'consent_webcam': False,
        'current_emotion': None,
        'emotion_confidence': 0.0,
        'chat_history': [],
        'emotion_analyzer': EmotionAnalyzer(),
        'detector': None,
        'conversation_engine': None,
        'webcam_active': False,
        'page': 'login'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ==================== AUTHENTIFICATION ====================

def show_login_page():
    """Affiche la page de connexion"""
    st.markdown('<h1 class="main-header">🎭 Emotion AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Votre assistant émotionnel intelligent</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Connexion", "📝 Inscription"])
        
        with tab1:
            with st.form("login_form"):
                st.subheader("Connexion")
                username = st.text_input("Nom d'utilisateur", key="login_username")
                password = st.text_input("Mot de passe", type="password", key="login_password")
                submit = st.form_submit_button("Se connecter", use_container_width=True)
                
                if submit:
                    if username and password:
                        db = get_db_session()
                        user = get_user_by_username(db, username)
                        
                        if user and verify_password(password, user.password_hash):
                            # Connexion réussie
                            update_user_login(db, user.id)
                            token = create_access_token(user.id, user.username)
                            
                            st.session_state['authenticated'] = True
                            st.session_state['user_id'] = user.id
                            st.session_state['username'] = user.username
                            st.session_state['token'] = token
                            st.session_state['consent_webcam'] = user.consent_webcam
                            st.session_state['page'] = 'dashboard'
                            
                            # Initialiser le moteur de conversation
                            api_key = os.getenv("ANTHROPIC_API_KEY")
                            st.session_state['conversation_engine'] = ConversationEngine(api_key)
                            
                            st.success("✅ Connexion réussie !")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Nom d'utilisateur ou mot de passe incorrect")
                        
                        db.close()
                    else:
                        st.warning("⚠️ Veuillez remplir tous les champs")
        
        with tab2:
            with st.form("register_form"):
                st.subheader("Créer un compte")
                new_username = st.text_input("Nom d'utilisateur", key="reg_username")
                new_email = st.text_input("Email", key="reg_email")
                new_password = st.text_input("Mot de passe", type="password", key="reg_password")
                confirm_password = st.text_input("Confirmer le mot de passe", type="password", key="reg_confirm")
                
                st.caption("Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule et un chiffre.")
                
                register = st.form_submit_button("S'inscrire", use_container_width=True)
                
                if register:
                    try:
                        # Validation
                        validate_registration(new_username, new_email, new_password, confirm_password)
                        
                        db = get_db_session()
                        
                        # Vérifier si l'utilisateur existe
                        if get_user_by_username(db, new_username):
                            st.error("❌ Ce nom d'utilisateur est déjà pris")
                        elif get_user_by_email(db, new_email):
                            st.error("❌ Cet email est déjà utilisé")
                        else:
                            # Créer l'utilisateur
                            hashed = hash_password(new_password)
                            user = create_user(db, new_username, new_email, hashed)
                            
                            st.success("✅ Compte créé avec succès ! Vous pouvez maintenant vous connecter.")
                        
                        db.close()
                        
                    except ValidationError as e:
                        st.error(f"❌ {str(e)}")

# ==================== DASHBOARD ====================

def show_dashboard():
    """Affiche le tableau de bord principal"""
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👋 Bonjour, {st.session_state['username']} !")
        
        st.markdown("---")
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["🏠 Dashboard", "📹 Détection", "💬 Chat IA", "📊 Statistiques", "⚙️ Paramètres"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Émotion actuelle
        if st.session_state['current_emotion']:
            emotion_fr = EMOTION_TRANSLATIONS.get(
                st.session_state['current_emotion'], 
                st.session_state['current_emotion']
            )
            st.markdown(f"""
            <div class="sidebar-info">
                <b>Émotion actuelle</b><br>
                <span style="font-size: 1.5rem">{emotion_fr}</span><br>
                <small>Confiance: {st.session_state['emotion_confidence']*100:.1f}%</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("🚪 Déconnexion", use_container_width=True):
            # Réinitialiser la session
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Contenu principal selon la page
    if "Dashboard" in page:
        show_home_dashboard()
    elif "Détection" in page:
        show_emotion_detection()
    elif "Chat" in page:
        show_chat_interface()
    elif "Statistiques" in page:
        show_statistics()
    elif "Paramètres" in page:
        show_settings()


def show_home_dashboard():
    """Page d'accueil du dashboard"""
    st.markdown('<h1 class="main-header">🎭 Tableau de Bord</h1>', unsafe_allow_html=True)
    
    # Récupérer les statistiques
    db = get_db_session()
    stats = get_emotion_statistics(db, st.session_state['user_id'], days=7)
    
    # Cards de statistiques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📊 Détections totales",
            stats.get('total_records', 0),
            help="Nombre total de détections émotionnelles"
        )
    
    with col2:
        dominant = stats.get('dominant_emotion')
        dominant_fr = EMOTION_TRANSLATIONS.get(dominant, "Aucune") if dominant else "Aucune"
        st.metric(
            "🎯 Émotion dominante",
            dominant_fr,
            help="Votre émotion la plus fréquente cette semaine"
        )
    
    with col3:
        dist = stats.get('distribution', {})
        happy_pct = dist.get('happy', {}).get('percentage', 0)
        st.metric(
            "😊 Taux de bonheur",
            f"{happy_pct}%",
            help="Pourcentage de détections 'heureux'"
        )
    
    with col4:
        conversations = get_conversation_history(db, st.session_state['user_id'])
        st.metric(
            "💬 Messages échangés",
            len(conversations),
            help="Total de messages avec l'assistant"
        )
    
    db.close()
    
    st.markdown("---")
    
    # Graphique d'évolution
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📈 Évolution émotionnelle (7 jours)")
        
        db = get_db_session()
        trend = get_emotion_trend(db, st.session_state['user_id'], days=7)
        db.close()
        
        if trend:
            df = pd.DataFrame(trend)
            
            # Créer un graphique
            fig = px.bar(
                df,
                x='date',
                y='total_detections',
                color='dominant_emotion',
                color_discrete_map={
                    'happy': '#4CAF50',
                    'sad': '#2196F3',
                    'angry': '#f44336',
                    'neutral': '#9E9E9E',
                    'surprise': '#FF9800',
                    'fear': '#9C27B0',
                    'disgust': '#795548'
                },
                labels={
                    'date': 'Date',
                    'total_detections': 'Nombre de détections',
                    'dominant_emotion': 'Émotion'
                }
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("📊 Pas encore de données. Commencez par utiliser la détection d'émotions !")
    
    with col2:
        st.subheader("🎯 Actions rapides")
        
        if st.button("📹 Démarrer la détection", use_container_width=True):
            st.session_state['page'] = 'detection'
            st.rerun()
        
        if st.button("💬 Parler à l'assistant", use_container_width=True):
            st.session_state['page'] = 'chat'
            st.rerun()
        
        st.markdown("---")
        
        st.subheader("💡 Conseil du jour")
        
        # Conseil basé sur l'émotion dominante
        tips = {
            'happy': "Profitez de cette belle énergie ! Partagez votre joie avec les autres. 🌟",
            'sad': "Accordez-vous du temps pour vous. Une petite promenade peut faire du bien. 💙",
            'angry': "La respiration profonde aide à calmer les tensions. Inspirez... Expirez... 🌬️",
            'neutral': "C'est le moment parfait pour essayer quelque chose de nouveau ! ✨",
            'fear': "Rappelez-vous : vous êtes plus fort(e) que vos peurs. Un pas à la fois. 💪"
        }
        
        dominant = stats.get('dominant_emotion', 'neutral')
        tip = tips.get(dominant, tips['neutral'])
        st.info(tip)


def show_emotion_detection():
    """Page de détection des émotions via webcam"""
    st.markdown('<h1 class="main-header">📹 Détection des Émotions</h1>', unsafe_allow_html=True)
    
    # Vérifier le consentement
    if not st.session_state['consent_webcam']:
        st.warning("""
        ⚠️ **Consentement requis**
        
        Pour utiliser la détection d'émotions, vous devez autoriser l'accès à votre webcam.
        Vos données émotionnelles sont privées et ne sont partagées avec personne.
        """)
        
        if st.button("✅ J'accepte l'utilisation de ma webcam", use_container_width=True):
            db = get_db_session()
            update_user_consent(db, st.session_state['user_id'], True)
            db.close()
            st.session_state['consent_webcam'] = True
            st.rerun()
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎥 Webcam en direct")
        
        # Placeholder pour la webcam
        video_placeholder = st.empty()
        
        # Contrôles
        start_col, stop_col = st.columns(2)
        
        with start_col:
            start_detection = st.button("▶️ Démarrer", use_container_width=True)
        
        with stop_col:
            stop_detection = st.button("⏹️ Arrêter", use_container_width=True)
        
        if stop_detection:
            st.session_state['webcam_active'] = False
        
        if start_detection:
            st.session_state['webcam_active'] = True
            
            # Initialiser le détecteur si nécessaire
            if st.session_state['detector'] is None:
                with st.spinner("Chargement du modèle de détection..."):
                    st.session_state['detector'] = EmotionDetector()
            
            # Capture webcam
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                st.error("❌ Impossible d'accéder à la webcam. Vérifiez qu'elle est connectée et autorisée.")
            else:
                detector = st.session_state['detector']
                analyzer = st.session_state['emotion_analyzer']
                db = get_db_session()
                
                frame_count = 0
                
                while st.session_state['webcam_active']:
                    ret, frame = cap.read()
                    
                    if not ret:
                        st.warning("⚠️ Problème de lecture de la webcam")
                        break
                    
                    # Détecter l'émotion toutes les 5 frames
                    if frame_count % 5 == 0:
                        result = detector.detect_emotion(frame)
                        
                        if result:
                            # Mettre à jour l'état
                            st.session_state['current_emotion'] = result.emotion
                            st.session_state['emotion_confidence'] = result.confidence
                            
                            # Ajouter à l'analyseur
                            analyzer.add_emotion(result)
                            
                            # Sauvegarder en base (toutes les 30 frames)
                            if frame_count % 30 == 0:
                                add_emotion_record(
                                    db,
                                    st.session_state['user_id'],
                                    result.emotion,
                                    result.confidence
                                )
                            
                            # Dessiner l'overlay
                            frame = detector.draw_emotion_overlay(frame, result)
                    
                    # Convertir BGR -> RGB pour l'affichage
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
                    
                    frame_count += 1
                    time.sleep(0.03)  # ~30 FPS
                
                cap.release()
                db.close()
    
    with col2:
        st.subheader("📊 Analyse en temps réel")
        
        if st.session_state['current_emotion']:
            emotion_fr = EMOTION_TRANSLATIONS.get(
                st.session_state['current_emotion'],
                st.session_state['current_emotion']
            )
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px;
                padding: 20px;
                color: white;
                text-align: center;
            ">
                <h2 style="margin: 0">{emotion_fr}</h2>
                <p style="margin: 10px 0 0 0">Confiance: {st.session_state['emotion_confidence']*100:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Suggestions basées sur l'émotion
            analyzer = st.session_state['emotion_analyzer']
            suggestions = analyzer.get_response_suggestions()
            
            st.markdown(f"**Tendance:** {suggestions.get('trend', 'stable')}")
            st.markdown(f"**Ton suggéré:** {suggestions.get('tone', 'neutral')}")
            
            if suggestions.get('approach'):
                st.markdown("**Approche recommandée:**")
                for approach in suggestions['approach'][:3]:
                    st.markdown(f"• {approach}")
        else:
            st.info("👀 Démarrez la détection pour voir l'analyse en temps réel")


def show_chat_interface():
    """Interface de chat avec l'assistant IA"""
    st.markdown('<h1 class="main-header">💬 Assistant Émoji</h1>', unsafe_allow_html=True)
    
    # Initialiser le moteur de conversation si nécessaire
    if st.session_state['conversation_engine'] is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        st.session_state['conversation_engine'] = ConversationEngine(api_key)
    
    engine = st.session_state['conversation_engine']
    
    # Mise à jour du contexte émotionnel
    if st.session_state['current_emotion']:
        engine.set_emotion_context(
            st.session_state['current_emotion'],
            st.session_state['emotion_confidence']
        )
    
    # Layout
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("😊 Votre état")
        
        if st.session_state['current_emotion']:
            emotion_fr = EMOTION_TRANSLATIONS.get(
                st.session_state['current_emotion'],
                "Non détecté"
            )
            st.markdown(f"**Émotion:** {emotion_fr}")
            st.markdown(f"**Confiance:** {st.session_state['emotion_confidence']*100:.1f}%")
        else:
            st.info("Utilisez la détection pour un chat personnalisé")
        
        st.markdown("---")
        
        if st.button("🗑️ Effacer l'historique", use_container_width=True):
            engine.clear_history()
            st.session_state['chat_history'] = []
            
            # Effacer aussi en base
            db = get_db_session()
            clear_conversation_history(db, st.session_state['user_id'])
            db.close()
            
            st.success("Historique effacé !")
            st.rerun()
        
        # Conseil bien-être
        if st.session_state['current_emotion']:
            st.markdown("---")
            st.subheader("💡 Conseil")
            tip = engine.generate_wellness_tip(st.session_state['current_emotion'])
            st.info(tip)
    
    with col1:
        # Conteneur de chat
        chat_container = st.container()
        
        with chat_container:
            # Afficher l'historique
            if not st.session_state['chat_history']:
                # Message d'accueil
                greeting = engine.get_greeting(st.session_state['current_emotion'])
                st.session_state['chat_history'].append({
                    'role': 'assistant',
                    'content': greeting
                })
            
            for message in st.session_state['chat_history']:
                if message['role'] == 'user':
                    with st.chat_message("user"):
                        st.write(message['content'])
                else:
                    with st.chat_message("assistant", avatar="🤗"):
                        st.write(message['content'])
        
        # Input utilisateur
        user_input = st.chat_input("Écrivez votre message...")
        
        if user_input:
            # Ajouter le message utilisateur
            st.session_state['chat_history'].append({
                'role': 'user',
                'content': user_input
            })
            
            # Sauvegarder en base
            db = get_db_session()
            add_conversation_message(
                db,
                st.session_state['user_id'],
                'user',
                user_input,
                st.session_state['current_emotion']
            )
            
            # Générer la réponse
            with st.spinner("Émoji réfléchit..."):
                response = engine.generate_response(
                    user_input,
                    st.session_state['current_emotion'],
                    st.session_state['emotion_confidence']
                )
            
            # Ajouter la réponse
            st.session_state['chat_history'].append({
                'role': 'assistant',
                'content': response
            })
            
            # Sauvegarder en base
            add_conversation_message(
                db,
                st.session_state['user_id'],
                'assistant',
                response,
                st.session_state['current_emotion']
            )
            
            db.close()
            st.rerun()


def show_statistics():
    """Page des statistiques émotionnelles"""
    st.markdown('<h1 class="main-header">📊 Statistiques Émotionnelles</h1>', unsafe_allow_html=True)
    
    db = get_db_session()
    
    # Sélection de la période
    period = st.selectbox(
        "Période d'analyse",
        ["7 derniers jours", "30 derniers jours", "90 derniers jours"],
        index=0
    )
    
    days = {"7 derniers jours": 7, "30 derniers jours": 30, "90 derniers jours": 90}[period]
    
    # Statistiques
    stats = get_emotion_statistics(db, st.session_state['user_id'], days=days)
    trend = get_emotion_trend(db, st.session_state['user_id'], days=days)
    
    if stats.get('total_records', 0) == 0:
        st.info("📊 Pas encore de données pour cette période. Utilisez la détection d'émotions pour commencer !")
        db.close()
        return
    
    # Métriques en haut
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total des détections", stats['total_records'])
    
    with col2:
        dominant_fr = EMOTION_TRANSLATIONS.get(stats['dominant_emotion'], stats['dominant_emotion'])
        st.metric("Émotion dominante", dominant_fr)
    
    with col3:
        # Calcul du "score de bien-être"
        dist = stats.get('distribution', {})
        positive = dist.get('happy', {}).get('percentage', 0)
        negative = (
            dist.get('sad', {}).get('percentage', 0) +
            dist.get('angry', {}).get('percentage', 0) +
            dist.get('fear', {}).get('percentage', 0)
        )
        wellbeing = max(0, min(100, 50 + positive - negative))
        st.metric("Score bien-être", f"{wellbeing:.0f}/100")
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🥧 Distribution des émotions")
        
        # Préparer les données
        dist_data = []
        for emotion, data in stats['distribution'].items():
            dist_data.append({
                'Émotion': EMOTION_TRANSLATIONS.get(emotion, emotion),
                'Pourcentage': data['percentage'],
                'Nombre': data['count']
            })
        
        if dist_data:
            df = pd.DataFrame(dist_data)
            
            fig = px.pie(
                df,
                values='Pourcentage',
                names='Émotion',
                color='Émotion',
                color_discrete_map={
                    '😊 Heureux': '#4CAF50',
                    '😢 Triste': '#2196F3',
                    '😠 En colère': '#f44336',
                    '😐 Neutre': '#9E9E9E',
                    '😲 Surpris': '#FF9800',
                    '😨 Peur': '#9C27B0',
                    '🤢 Dégoût': '#795548'
                }
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📈 Évolution quotidienne")
        
        if trend:
            df = pd.DataFrame(trend)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['date'],
                y=df['total_detections'],
                mode='lines+markers',
                name='Détections',
                line=dict(color='#667eea', width=3),
                marker=dict(size=10)
            ))
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Nombre de détections",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Tableau détaillé
    st.markdown("---")
    st.subheader("📋 Détail par émotion")
    
    detail_data = []
    for emotion, data in stats['distribution'].items():
        detail_data.append({
            'Émotion': EMOTION_TRANSLATIONS.get(emotion, emotion),
            'Occurrences': data['count'],
            'Pourcentage': f"{data['percentage']}%",
            'Confiance moyenne': f"{data['avg_confidence']*100:.1f}%"
        })
    
    if detail_data:
        df = pd.DataFrame(detail_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    db.close()


def show_settings():
    """Page des paramètres utilisateur"""
    st.markdown('<h1 class="main-header">⚙️ Paramètres</h1>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👤 Informations du compte")
        
        db = get_db_session()
        user = get_user_by_username(db, st.session_state['username'])
        
        if user:
            st.text_input("Nom d'utilisateur", value=user.username, disabled=True)
            st.text_input("Email", value=user.email, disabled=True)
            st.text_input("Membre depuis", value=user.created_at.strftime("%d/%m/%Y"), disabled=True)
            
            last_login = user.last_login.strftime("%d/%m/%Y %H:%M") if user.last_login else "Jamais"
            st.text_input("Dernière connexion", value=last_login, disabled=True)
        
        db.close()
    
    with col2:
        st.subheader("🔒 Confidentialité")
        
        st.markdown("""
        **Consentement webcam**
        
        Vos données émotionnelles sont privées et ne sont jamais partagées.
        Vous pouvez révoquer votre consentement à tout moment.
        """)
        
        consent = st.checkbox(
            "J'autorise l'utilisation de ma webcam pour la détection d'émotions",
            value=st.session_state['consent_webcam']
        )
        
        if consent != st.session_state['consent_webcam']:
            db = get_db_session()
            update_user_consent(db, st.session_state['user_id'], consent)
            db.close()
            st.session_state['consent_webcam'] = consent
            st.success("✅ Préférence mise à jour !")
    
    st.markdown("---")
    
    # Zone danger
    st.subheader("⚠️ Zone de danger")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Effacer mon historique émotionnel", use_container_width=True):
            if st.session_state.get('confirm_delete_emotions'):
                db = get_db_session()
                # Supprimer les émotions
                from database.models import EmotionRecord
                db.query(EmotionRecord).filter(
                    EmotionRecord.user_id == st.session_state['user_id']
                ).delete()
                db.commit()
                db.close()
                
                st.success("✅ Historique émotionnel effacé !")
                st.session_state['confirm_delete_emotions'] = False
            else:
                st.session_state['confirm_delete_emotions'] = True
                st.warning("⚠️ Cliquez à nouveau pour confirmer")
    
    with col2:
        if st.button("🗑️ Effacer mes conversations", use_container_width=True):
            if st.session_state.get('confirm_delete_conversations'):
                db = get_db_session()
                clear_conversation_history(db, st.session_state['user_id'])
                db.close()
                
                st.session_state['chat_history'] = []
                if st.session_state['conversation_engine']:
                    st.session_state['conversation_engine'].clear_history()
                
                st.success("✅ Conversations effacées !")
                st.session_state['confirm_delete_conversations'] = False
            else:
                st.session_state['confirm_delete_conversations'] = True
                st.warning("⚠️ Cliquez à nouveau pour confirmer")

# ==================== MAIN ====================

def main():
    """Point d'entrée principal de l'application"""
    
    if not st.session_state['authenticated']:
        show_login_page()
    else:
        show_dashboard()


if __name__ == "__main__":
    main()
