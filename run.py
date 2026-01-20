#!/usr/bin/env python3
"""
Script de lancement de l'application Emotion AI
"""

import subprocess
import sys
import os

def check_dependencies():
    """Vérifie que les dépendances sont installées"""
    try:
        import streamlit
        import cv2
        import numpy
        import sqlalchemy
        import bcrypt
        print("✅ Dépendances principales installées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("\nInstallez les dépendances avec:")
        print("  pip install -r requirements.txt")
        return False

def check_env():
    """Vérifie la configuration"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your-anthropic-api-key-here":
        print("⚠️  Clé API Anthropic non configurée")
        print("   Le chat IA fonctionnera en mode limité")
        print("   Configurez ANTHROPIC_API_KEY dans .env pour une expérience complète")
    else:
        print("✅ Clé API Anthropic configurée")
    
    jwt_key = os.getenv("JWT_SECRET_KEY")
    if not jwt_key or jwt_key == "change-this-to-a-very-long-random-string-in-production":
        print("⚠️  Clé JWT par défaut utilisée - Changez-la en production!")
    else:
        print("✅ Clé JWT personnalisée configurée")

def init_db():
    """Initialise la base de données"""
    from database import init_database
    init_database()

def run_app():
    """Lance l'application Streamlit"""
    print("\n" + "="*50)
    print("🎭 Démarrage de Emotion AI...")
    print("="*50 + "\n")
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "app.py",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ])

def main():
    """Point d'entrée principal"""
    print("="*50)
    print("🎭 Emotion AI - Vérification pré-lancement")
    print("="*50 + "\n")
    
    # Vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Charger et vérifier .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
        check_env()
    except ImportError:
        print("⚠️  python-dotenv non installé, variables d'environnement système utilisées")
    
    # Initialiser la base de données
    print("\n📦 Initialisation de la base de données...")
    init_db()
    
    # Lancer l'application
    run_app()

if __name__ == "__main__":
    main()
