@echo off
REM Compartir Ensenando con un enlace - doble clic para usarlo
REM Levanta la version web en este computador (con el MongoDB local)
REM y la publica con un enlace temporal de Cloudflare.
REM El enlace funciona mientras esta ventana siga abierta.

setlocal
cd /d "%~dp0"
title Ensenando - compartir

set "PY=venv\Scripts\python.exe"
set "PORT=5000"
set "SERVER_LOG=%TEMP%\ensenando-servidor.log"
set "TUNNEL_LOG=%TEMP%\ensenando-tunel.log"
set "URL_FILE=%TEMP%\ensenando-enlace.txt"

echo.
echo  ==========================================
echo    Ensenando - compartir con un enlace
echo  ==========================================
echo.

REM ---- 1. Entorno de Python ----
if not exist "%PY%" (
    echo [1/5] No existe el entorno virtual. Instalando, puede tardar unos minutos...
    python -m venv venv
    if errorlevel 1 goto :error_python
    "%PY%" -m pip install --upgrade pip
    "%PY%" -m pip install -r requirements.txt
    if errorlevel 1 goto :error_pip
) else (
    echo [1/5] Entorno de Python listo.
)

"%PY%" -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo       Falta Flask. Instalando...
    "%PY%" -m pip install "Flask>=3.0"
    if errorlevel 1 goto :error_pip
)

REM ---- 2. MongoDB local ----
"%PY%" -c "from pymongo import MongoClient; from src.config import MONGO_URI; MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000).admin.command('ping')" >nul 2>&1
if errorlevel 1 goto :error_mongo
echo [2/5] MongoDB local encendido.

REM ---- 3. Cloudflare Tunnel ----
set "CF="
for /f "delims=" %%i in ('where cloudflared 2^>nul') do if not defined CF set "CF=%%i"
if not defined CF if exist "%ProgramFiles(x86)%\cloudflared\cloudflared.exe" set "CF=%ProgramFiles(x86)%\cloudflared\cloudflared.exe"
if not defined CF if exist "%ProgramFiles%\cloudflared\cloudflared.exe" set "CF=%ProgramFiles%\cloudflared\cloudflared.exe"
if not defined CF (
    echo [3/5] Instalando Cloudflare Tunnel...
    winget install --id Cloudflare.cloudflared -e --accept-source-agreements --accept-package-agreements
    if exist "%ProgramFiles(x86)%\cloudflared\cloudflared.exe" set "CF=%ProgramFiles(x86)%\cloudflared\cloudflared.exe"
    if exist "%ProgramFiles%\cloudflared\cloudflared.exe" set "CF=%ProgramFiles%\cloudflared\cloudflared.exe"
)
if not defined CF goto :error_cloudflared
echo [3/5] Cloudflare Tunnel listo.

REM ---- 4. Servidor web ----
powershell -NoProfile -Command "try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:%PORT%/health -TimeoutSec 2 | Out-Null; exit 0 } catch { exit 1 }"
if not errorlevel 1 goto :error_port

echo [4/5] Iniciando el servidor web (la primera vez puede tardar un poco)...
start "" /b "%PY%" web_server.py > "%SERVER_LOG%" 2>&1
powershell -NoProfile -Command "for ($i = 0; $i -lt 90; $i++) { try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:%PORT%/health -TimeoutSec 2 | Out-Null; exit 0 } catch { Start-Sleep 1 } }; exit 1"
if errorlevel 1 goto :error_server

REM ---- 5. Enlace publico ----
echo [5/5] Creando el enlace...
if exist "%URL_FILE%" del "%URL_FILE%"
start "" /b "%CF%" tunnel --no-autoupdate --url http://localhost:%PORT% > "%TUNNEL_LOG%" 2>&1
powershell -NoProfile -Command "for ($i = 0; $i -lt 60; $i++) { $m = Select-String -Path '%TUNNEL_LOG%' -Pattern 'https://[a-z0-9-]+\.trycloudflare\.com' -ErrorAction SilentlyContinue | Select-Object -First 1; if ($m -and (Select-String -Path '%TUNNEL_LOG%' -Pattern 'Registered tunnel connection' -Quiet)) { $m.Matches[0].Value | Out-File -Encoding ascii '%URL_FILE%'; exit 0 }; Start-Sleep 1 }; exit 1"
if errorlevel 1 goto :error_tunnel
set /p URL=<"%URL_FILE%"

echo %URL%| clip
echo.
echo  ==========================================
echo    LISTO. Comparte este enlace:
echo.
echo    %URL%
echo.
echo    (ya quedo copiado, pegalo con Ctrl+V)
echo  ==========================================
echo.
echo  - Abrelo en Chrome o Edge y permite camara y microfono.
echo  - Las cuentas se guardan en el MongoDB de ESTE computador.
echo  - El enlace funciona mientras esta ventana siga abierta.
echo  - Cada vez que abras compartir.bat el enlace sera distinto.
echo.
start "" "%URL%"
echo  Presiona cualquier tecla para CERRAR el enlace...
pause >nul
goto :stop

:error_python
echo.
echo  [ERROR] No se encontro Python. Instala Python 3 y vuelve a intentarlo.
goto :end

:error_pip
echo.
echo  [ERROR] No se pudieron instalar las dependencias. Revisa tu conexion a internet.
goto :end

:error_mongo
echo.
echo  [ERROR] MongoDB no esta encendido en este computador.
echo          Abre MongoDB (o el servicio "MongoDB Server") y vuelve a intentarlo.
goto :end

:error_cloudflared
echo.
echo  [ERROR] No se pudo instalar Cloudflare Tunnel.
echo          Instalalo con: winget install Cloudflare.cloudflared
goto :end

:error_port
echo.
echo  [ERROR] Ya hay un servidor usando el puerto %PORT%.
echo          Puede que compartir.bat ya este abierto en otra ventana.
goto :end

:error_server
echo.
echo  [ERROR] El servidor web no arranco. Detalles en:
echo          %SERVER_LOG%
goto :stop

:error_tunnel
echo.
echo  [ERROR] No se pudo crear el enlace. Revisa tu conexion a internet.
echo          Detalles en: %TUNNEL_LOG%
goto :stop

:stop
echo.
echo  Cerrando el enlace y el servidor...
taskkill /f /im cloudflared.exe >nul 2>&1
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort %PORT% -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }"
echo  Listo, el enlace ya no funciona.

:end
echo.
pause
endlocal
