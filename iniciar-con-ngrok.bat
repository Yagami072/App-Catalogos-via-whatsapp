@echo off
REM Configurar ngrok y el servidor multimedia

echo.
echo ==============================================================
echo     Servidor Multimedia con ngrok - Blancos Primavera
echo ==============================================================
echo.

REM Verificar si ngrok está instalado
where ngrok >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: ngrok no está instalado
    echo.
    echo Descarga ngrok desde: https://ngrok.com/download
    echo.
    echo Después de instalarlo:
    echo 1. Crea una cuenta en https://dashboard.ngrok.com/signup
    echo 2. Obtén tu auth token desde https://dashboard.ngrok.com/auth/your-authtoken
    echo 3. Ejecuta: ngrok config add-authtoken YOUR_TOKEN_HERE
    echo.
    pause
    exit /b 1
)

echo ✅ ngrok detectado
echo.
echo Iniciando túnel ngrok en puerto 5000...
echo.

REM Iniciar ngrok en background
start cmd /c "ngrok http 5000 --log stdout 2>&1 | tee ngrok.log"

echo ✅ Túnel ngrok iniciado
echo.
echo Esperando a que se estabilice...
timeout /t 3 /nobreak

echo.
echo 📨 Tu URL pública es:
echo.

REM Esperar a que ngrok esté listo y extraer la URL
for /f "tokens=*" %%i in ('curl -s http://localhost:4040/api/tunnels ^| findstr /R "public_url"') do (
    echo %%i
)

echo.
echo Ahora iniciando el servidor Flask...
echo.

python app.py

pause
