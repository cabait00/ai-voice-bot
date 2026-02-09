@echo off
echo ============================================
echo  PGN-plus-P Voice Agent - Setup
echo ============================================
echo.

REM Prüfe ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python ist nicht installiert!
    echo Bitte installiere Python 3.10 oder neuer von python.org
    pause
    exit /b 1
)

REM Prüfe ob Node.js installiert ist
node --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Node.js ist nicht installiert!
    echo Bitte installiere Node.js 18 oder neuer von nodejs.org
    pause
    exit /b 1
)

echo [1/6] Python Version:
python --version
echo.

echo [2/6] Node.js Version:
node --version
echo.

echo [3/6] Erstelle Virtual Environment...
python -m venv venv
echo ✓ Virtual Environment erstellt
echo.

echo [4/6] Aktiviere Virtual Environment...
call venv\Scripts\activate.bat
echo ✓ Virtual Environment aktiviert
echo.

echo [5/6] Installiere Python Dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo ✓ Python Dependencies installiert
echo.

echo [6/6] Erstelle .env Datei...
if not exist .env (
    copy .env.example .env
    echo ✓ .env Datei erstellt
    echo.
    echo [WICHTIG] Bitte setze deinen OpenAI API Key in der .env Datei:
    echo   Öffne .env und ersetze "add-your-key-here" mit deinem echten API Key
) else (
    echo ✓ .env Datei existiert bereits
)
echo.

echo ============================================
echo  Setup abgeschlossen!
echo ============================================