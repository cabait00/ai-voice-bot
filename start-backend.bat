@echo off
echo ============================================
echo  Starting PGN-plus-P Backend
echo ============================================
echo.

REM Prüfe ob venv existiert
if not exist venv (
    echo [FEHLER] Virtual Environment nicht gefunden!
    echo Bitte führe zuerst setup.bat aus.
    pause
    exit /b 1
)

REM Prüfe ob .env existiert
if not exist .env (
    echo [FEHLER] .env Datei nicht gefunden!
    echo Bitte führe zuerst setup.bat aus.
    pause
    exit /b 1
)

REM Prüfe ob product_data.json existiert
if not exist product_data.json (
    echo [INFO] Produktdaten nicht gefunden
    echo [1/2] Lade Produktdaten...
    call venv\Scripts\activate.bat
    python -m app.scraper
    echo.
)

echo [2/2] Starte Backend Server...
call venv\Scripts\activate.bat
python main.py

pause
