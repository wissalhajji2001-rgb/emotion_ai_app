# 🚀 Guide de Démarrage Rapide - Emotion AI

## Installation en 5 minutes

### Étape 1 : Prérequis

Assurez-vous d'avoir :
- ✅ Python 3.9+ installé
- ✅ Une webcam fonctionnelle
- ✅ Une clé API Anthropic (optionnelle mais recommandée)

### Étape 2 : Installation

```bash
# 1. Téléchargez le projet
cd emotion_ai_app

# 2. Créez un environnement virtuel
python -m venv venv

# 3. Activez-le
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Installez les dépendances
pip install -r requirements.txt
```

### Étape 3 : Configuration

```bash
# Copiez le fichier de configuration
cp .env.example .env

# Éditez-le avec votre clé API
nano .env
# ou
notepad .env  # Windows
```

Ajoutez votre clé API Anthropic :
```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...
```

> 💡 **Pas de clé API ?** L'app fonctionne quand même avec des réponses pré-définies !

### Étape 4 : Lancement

```bash
# Option 1 : Script automatique
python run.py

# Option 2 : Direct Streamlit
streamlit run app.py
```

### Étape 5 : Accès

Ouvrez votre navigateur à : **http://localhost:8501**

---

## 🎮 Première utilisation

### 1. Créer un compte

1. Cliquez sur l'onglet **📝 Inscription**
2. Remplissez :
   - Nom d'utilisateur (3-20 caractères)
   - Email valide
   - Mot de passe (8+ caractères, 1 majuscule, 1 minuscule, 1 chiffre)
3. Cliquez sur **S'inscrire**

### 2. Se connecter

1. Entrez votre nom d'utilisateur et mot de passe
2. Cliquez sur **Se connecter**

### 3. Activer la détection

1. Allez dans **📹 Détection**
2. Acceptez le consentement webcam
3. Cliquez sur **▶️ Démarrer**
4. Votre émotion apparaît en temps réel !

### 4. Parler à l'assistant

1. Allez dans **💬 Chat IA**
2. Écrivez votre message
3. L'assistant adapte son ton selon votre émotion

---

## ❓ Problèmes fréquents

### "Module not found"

```bash
pip install -r requirements.txt
```

### "Webcam non détectée"

1. Vérifiez la connexion physique
2. Autorisez l'accès dans les paramètres du navigateur
3. Fermez les autres apps utilisant la webcam

### "Erreur API Claude"

- Vérifiez votre clé API dans `.env`
- L'app fonctionne sans, avec des réponses pré-définies

---

## 📞 Support

- 📖 Documentation complète : `README.md`
- 🏗 Architecture : `docs/ARCHITECTURE.md`
- 🐛 Problèmes : Ouvrez une issue sur GitHub
