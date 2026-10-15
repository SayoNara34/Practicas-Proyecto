@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Primero instala el proyecto siguiendo INSTRUCCIONES_WEB.md.
  echo Necesitas crear el entorno .venv e instalar requirements.txt.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" ejecutar.py
if errorlevel 1 pause
