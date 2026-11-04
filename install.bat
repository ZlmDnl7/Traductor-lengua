@echo off
REM Script de instalacion - Ensenando
REM Ejecutar desde la raiz del proyecto

echo Creando entorno virtual (si no existe)...
if not exist "venv" (
    python -m venv venv
)

echo Activando venv e instalando dependencias...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Instalacion finalizada. Para ejecutar la aplicacion:
echo   venv\Scripts\activate
echo   python run.py
pause
