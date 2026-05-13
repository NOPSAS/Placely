@echo off
echo Starter Placely XDi API...
echo.

cd /d "%~dp0..\xdi"

if not exist .env (
    echo ADVARSEL: .env-fil ikke funnet.
    echo Kopier .env.example til .env og legg inn ANTHROPIC_API_KEY
    echo.
    pause
    exit /b 1
)

if not exist venv (
    echo Oppretter virtuelt miljø...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo XDi starter på http://localhost:8001
echo API-dokumentasjon: http://localhost:8001/docs
echo Trykk Ctrl+C for å stoppe
echo.

python main.py
