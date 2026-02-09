@echo off
echo ============================================
echo  Starting PGN-plus-P Frontend
echo ============================================
echo.

cd frontend

REM Prüfe ob node_modules existiert
if not exist node_modules (
    echo [INFO] node_modules nicht gefunden
    echo [1/2] Installiere Dependencies...
    call npm install
    echo.
)

echo [2/2] Starte Frontend Dev Server...
call npm run dev

pause
