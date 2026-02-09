@echo off
echo ============================================
echo  PGN-plus-P Voice Agent - Start All
echo ============================================
echo.

REM Prüfe ob Setup durchgeführt wurde
if not exist venv (
    echo [FEHLER] Bitte führe zuerst setup.bat aus!
    pause
    exit /b 1
)

if not exist .env (
    echo [FEHLER] Bitte führe zuerst setup.bat aus!
    pause
    exit /b 1
)

echo [INFO] Starte Backend und Frontend in separaten Fenstern...
echo.

REM Starte Backend in neuem Fenster
echo [1/2] Starte Backend...
start "Backend Server" cmd /k start-backend.bat

REM Warte 3 Sekunden damit Backend zuerst startet
timeout /t 3 /nobreak >nul

REM Starte Frontend in neuem Fenster
echo [2/2] Starte Frontend...
start "Frontend Dev Server" cmd /k start-frontend.bat

echo.
echo ============================================
echo  Beide Server wurden gestartet!
echo ============================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Drücke eine beliebige Taste zum Schließen...
pause >nul
