@echo off
echo ============================================
echo  Cleanup - Loesche alle Installationen
echo ============================================
echo.

echo [INFO] Loesche Virtual Environment...
if exist venv (
    rmdir /s /q venv
    echo ✓ venv geloescht
) else (
    echo [INFO] Kein venv gefunden
)
echo.

echo [INFO] Loesche ChromaDB...
if exist chroma_db (
    rmdir /s /q chroma_db
    echo ✓ chroma_db geloescht
) else (
    echo [INFO] Keine ChromaDB gefunden
)
echo.

echo [INFO] Loesche __pycache__...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo ✓ __pycache__ geloescht
echo.

echo ============================================
echo  Cleanup abgeschlossen!
echo ============================================
echo.
echo Fuehre jetzt setup.bat aus fuer Neuinstallation.
echo.
pause