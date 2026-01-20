@echo off
echo ========================================
echo    Emotion AI - Installation Windows
echo ========================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH
    echo Telechargez Python depuis https://python.org
    pause
    exit /b 1
)

echo [OK] Python detecte
echo.

REM Créer environnement virtuel
echo Creation de l'environnement virtuel...
python -m venv venv
if errorlevel 1 (
    echo [ERREUR] Impossible de creer l'environnement virtuel
    pause
    exit /b 1
)

echo [OK] Environnement virtuel cree
echo.

REM Activer l'environnement
call venv\Scripts\activate.bat

REM Mettre à jour pip
echo Mise a jour de pip...
python -m pip install --upgrade pip

REM Installer les dépendances légères
echo.
echo Installation des dependances (version legere)...
echo Cela peut prendre quelques minutes...
echo.
pip install -r requirements_light.txt

if errorlevel 1 (
    echo.
    echo [ERREUR] Probleme lors de l'installation
    echo Essayez d'installer manuellement:
    echo   pip install streamlit opencv-python-headless anthropic
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Installation terminee avec succes!
echo ========================================
echo.
echo Pour lancer l'application:
echo   1. Ouvrez un terminal dans ce dossier
echo   2. Tapez: venv\Scripts\activate
echo   3. Tapez: streamlit run app.py
echo.
echo N'oubliez pas de configurer votre cle API Anthropic dans .env
echo.
pause
