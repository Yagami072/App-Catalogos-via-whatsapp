@echo off
REM Servidor Multimedia Blancos Primavera - Windows Startup Script

echo.
echo ==============================================================
echo     Servidor Multimedia - Blancos Primavera
echo ==============================================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Descarga Python desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo Iniciando servidor...
echo.
echo    API disponible en: http://localhost:5000
echo    Carpeta de uploads: uploads\
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python app.py

pause
