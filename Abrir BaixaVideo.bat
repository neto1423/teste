@echo off
cd /d "%~dp0"
start "BaixaVideo - servidor" cmd.exe /k "py app.py"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8000"
