# emotion_ai_app
Application d'analyse des émotions par IA
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<h1 align="center">🎭 Emotion AI</h1>

<p align="center">
  <strong>Assistant émotionnel intelligent avec détection d'émotions en temps réel</strong>
</p>

<p align="center">
  <a href="#-fonctionnalités">Fonctionnalités</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-utilisation">Utilisation</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-technologies">Technologies</a>
</p>

---

## 📖 Description

**Emotion AI** est une application web complète qui combine la **détection d'émotions faciales en temps réel** avec un **assistant conversationnel intelligent**. L'assistant adapte ses réponses en fonction de votre état émotionnel détecté, offrant une expérience personnalisée et empathique.

### Cas d'utilisation

- 🧘 **Bien-être personnel** : Suivi de vos émotions au quotidien
- 💬 **Soutien émotionnel** : Conversations adaptées à votre humeur
- 📊 **Auto-analyse** : Statistiques et tendances émotionnelles
- 🎓 **Éducatif** : Comprendre et gérer ses émotions

---

## ✨ Fonctionnalités

### 🔐 Authentification sécurisée
- Inscription et connexion avec validation
- Mots de passe hashés avec bcrypt
- Tokens JWT pour les sessions

### 🎥 Détection d'émotions en temps réel
- Analyse faciale via webcam
- 7 émotions détectées : 😊 Heureux, 😢 Triste, 😠 En colère, 😐 Neutre, 😲 Surpris, 😨 Peur, 🤢 Dégoût
- Stabilisation des détections pour plus de précision

### 🤖 Chat IA empathique
- Intégration avec Groq (gratuit) ou Anthropic Claude
- Réponses adaptées à l'état émotionnel
- Conseils bien-être personnalisés

### 📊 Statistiques et analyses
- Distribution des émotions (graphique circulaire)
- Évolution temporelle (courbes)
- Score de bien-être calculé
- Export des données

### ⚙️ Personnalisation
- Gestion du consentement webcam
- Effacement des données personnelles
- Thème visuel moderne

---

## 🚀 Installation

### Prérequis

- Python 3.10 ou supérieur
- Webcam (optionnel, pour la détection d'émotions)
- Clé API Groq (gratuite) ou Anthropic

### Installation rapide (Windows)

```bash
# Cloner le projet
git clone https://github.com/wissalhajji2001-rgb/emotion_ai_app.git
cd emotion_ai_app

# Exécuter le script d'installation
install_windows.bat
```

### Installation manuelle

```bash
# 1. Cloner le projet
git clone https://github.com/wissalhajji2001-rgb/emotion_ai_app.git
cd emotion_ai_app

# 2. Créer un environnement virtuel
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# Ou version légère (sans TensorFlow)
pip install -r requirements_light.txt
```

### Configuration

```bash
# Copier le fichier de configuration
cp .env.example .env

# Éditer .env avec vos clés API
```

Contenu du fichier `.env` :

```env
# API Gratuite (recommandée)
GROQ_API_KEY=gsk_votre_cle_groq

# Ou API Anthropic (payante)
ANTHROPIC_API_KEY=sk-ant-votre_cle_anthropic

# Sécurité
JWT_SECRET_KEY=votre_cle_secrete_32_caracteres

# Base de données
DATABASE_URL=sqlite:///emotion_ai.db
```

---

## 💻 Utilisation

### Démarrer l'application

```bash
# Méthode simple
streamlit run app.py

# Ou via le script
python run.py
```

L'application sera accessible à : **http://localhost:8501**

### Première utilisation

1. **Créer un compte** : Inscrivez-vous avec un nom d'utilisateur et mot de passe
2. **Consentement** : Autorisez l'accès à la webcam (optionnel)
3. **Dashboard** : Accédez aux fonctionnalités principales
4. **Détection** : Lancez la détection d'émotions
5. **Chat** : Discutez avec l'assistant IA

---

## 🏗 Architecture

```
emotion_ai_app/
│
├── 📄 app.py                    # Application principale Streamlit
├── 📄 run.py                    # Script de lancement
├── 📄 requirements.txt          # Dépendances complètes
├── 📄 requirements_light.txt    # Dépendances légères
├── 📄 .env.example              # Template de configuration
│
├── 📁 auth/                     # Module d'authentification
│   ├── __init__.py
│   └── authentication.py        # Hash, JWT, validation
│
├── 📁 database/                 # Module base de données
│   ├── __init__.py
│   ├── models.py                # Modèles SQLAlchemy
│   └── crud.py                  # Opérations CRUD
│
├── 📁 emotion_detection/        # Module détection
│   ├── __init__.py
│   └── detector.py              # Détecteur OpenCV/FER
│
├── 📁 conversation_engine/      # Module chat IA
│   ├── __init__.py
│   └── engine.py                # Intégration LLM
│
├── 📁 ui/                       # Composants interface
│   └── __init__.py
│
├── 📁 docs/                     # Documentation
│   ├── ARCHITECTURE.md
│   └── QUICKSTART.md
│
└── 📁 .streamlit/               # Config Streamlit
    └── config.toml
```

---

## 🛠 Technologies

| Catégorie | Technologies |
|-----------|--------------|
| **Frontend** | Streamlit, Plotly, CSS custom |
| **Backend** | Python 3.10+, SQLAlchemy |
| **IA/ML** | OpenCV, Haar Cascades |
| **LLM** | Groq API, Anthropic Claude |
| **Auth** | bcrypt, PyJWT |
| **Database** | SQLite |
| **Webcam** | streamlit-webrtc, av |

---

## 🎭 Émotions détectées

| Émotion | Emoji | Couleur | Description |
|---------|-------|---------|-------------|
| Happy | 😊 | 🟢 Vert | Joie, sourire |
| Sad | 😢 | 🔵 Bleu | Tristesse |
| Angry | 😠 | 🔴 Rouge | Colère |
| Neutral | 😐 | ⚪ Gris | Neutre |
| Surprise | 😲 | 🟡 Jaune | Étonnement |
| Fear | 😨 | 🟣 Violet | Peur |
| Disgust | 🤢 | 🟤 Marron | Dégoût |

---

## 📈 Captures d'écran

### Page de connexion
> Interface moderne avec onglets Connexion/Inscription

### Dashboard principal
> Accès rapide à toutes les fonctionnalités

### Détection d'émotions
> Affichage en temps réel avec graphiques

### Statistiques
> Visualisation des tendances émotionnelles

---

## 🔒 Sécurité & Confidentialité

- ✅ **Données locales** : Stockage uniquement en local (SQLite)
- ✅ **Mots de passe hashés** : Algorithme bcrypt sécurisé
- ✅ **Consentement explicite** : Activation webcam contrôlée
- ✅ **Suppression des données** : Option d'effacement complet
- ✅ **Aucun envoi cloud** : Les images ne quittent pas votre machine

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Voici comment participer :

1. **Fork** le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une **Pull Request**

---

<p align="center">
  Fait avec ❤️ par Wissal HAJJI et Ali BADIDI
</p>

