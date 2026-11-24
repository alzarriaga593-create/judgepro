@echo off
title EASY REFEREE
cd /d "%~dp0"
echo ======================================
echo  EASY REFEREE
echo  Buscando IP de hoy...
echo ======================================

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set IP=%%a
set IP=%IP: =%

echo Tu IP de hoy es: %IP%
echo Prendiendo servidor en %IP%:8001...
echo.

REM - Prende el server en OTRA ventana VISIBLE para ver si da error
start "SERVIDOR EASY REFEREE" python server.py

timeout /t 3 /nobreak >nul
echo Abriendo navegador...
start "" "http://%IP%:8001/index.html"
echo.
echo LISTO. NO CIERRES NINGUNA VENTANA NEGRA.
echo Tienes que tener 2 ventanas negras abiertas:
echo 1. Esta (EASY REFEREE)
echo 2. La que dice SERVIDOR EASY REFEREE
echo.
pause