@echo off
setlocal

REM Define las rutas
set VENV_DIR=%cd%\venv
set APP_DIR=%cd%
set SHORTCUT_NAME=Youtube_Downloader.bat
set DESKTOP_DIR=%USERPROFILE%\Desktop

REM Crear el entorno virtual
echo Creando entorno virtual en %VENV_DIR%...
python -m venv %VENV_DIR%

REM Activar el entorno virtual
echo Activando entorno virtual...
call %VENV_DIR%\Scripts\activate.bat

REM Instalar los requirements
echo Instalando dependencias de requirements.txt...
pip install -r requirements.txt

REM Habilitar la ejecución de scripts de PowerShell
echo Habilitando la ejecución de scripts de PowerShell...
powershell -Command "Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force"

REM Habilitar el puerto 5000 en el Firewall
echo Habilitando el puerto 5000 en el Firewall...
powershell -Command "New-NetFirewallRule -DisplayName 'Abrir puerto 5000' -Direction Inbound -LocalPort 5000 -Protocol TCP -Action Allow"

REM Crear un archivo .bat en el escritorio para ejecutar app.py
echo Creando archivo .bat en el escritorio para ejecutar la aplicación...

(
    echo @echo off
    echo cd /d "%APP_DIR%"
    echo call "%VENV_DIR%\Scripts\activate.bat"
    echo python app.py
    echo timeout /t 3 /nobreak >nul  REM Esperar 3 segundos para que el servidor se inicie
    echo start http://127.0.0.1:5000  REM Abrir el navegador en 127.0.0.1:5000
    echo pause
) > "%DESKTOP_DIR%\%SHORTCUT_NAME%"

echo Acceso directo creado en el escritorio: %DESKTOP_DIR%\%SHORTCUT_NAME%

echo Proceso completado.
pause
