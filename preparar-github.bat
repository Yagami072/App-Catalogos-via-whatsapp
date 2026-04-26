@echo off
REM Script para preparar los archivos para GitHub/Streamlit

setlocal enabledelayedexpansion

echo.
echo ==============================================================
echo    Preparador de Archivos - Servidor Multimedia Streamlit
echo ==============================================================
echo.

REM Detectar la ruta actual
set CURRENT_DIR=%cd%

echo Tu repositorio: https://github.com/Yagami072/App-Catalogos-via-whatsapp
echo.
echo Archivos a copiar:
echo   - streamlit_app.py
echo   - requirements.txt
echo   - .streamlit/config.toml
echo   - DEPLOYMENT-STREAMLIT.md
echo   - QUICK-START.md
echo.

REM Verificar que los archivos existan
if not exist "streamlit_app.py" (
    echo ERROR: No encontre streamlit_app.py en %CURRENT_DIR%
    echo Asegúrate de estar en la carpeta: servidor-multimedia
    pause
    exit /b 1
)

echo ✅ Archivos encontrados
echo.
echo PRÓXIMOS PASOS:
echo.
echo 1. Git Clone (si no lo has hecho):
echo    git clone https://github.com/Yagami072/App-Catalogos-via-whatsapp.git
echo    cd App-Catalogos-via-whatsapp
echo.
echo 2. Copia estos archivos a la raíz de tu repo:
echo    - streamlit_app.py
echo    - requirements.txt
echo    - .streamlit/config.toml (crear carpeta .streamlit si no existe)
echo.
echo 3. Sube a GitHub:
echo    git add .
echo    git commit -m "Agregar servidor multimedia Streamlit"
echo    git push origin main
echo.
echo 4. Ve a https://streamlit.io/cloud y haz deploy
echo.
echo 5. Usa la URL en tu app React
echo.
echo ==============================================================
echo.
echo ¿Deseas ver la guía completa? (DEPLOYMENT-STREAMLIT.md)
echo.
pause

type DEPLOYMENT-STREAMLIT.md
