#!/bin/bash
set -e

cd "$(dirname "$0")/../xdi"

if [ ! -f .env ]; then
  echo "ADVARSEL: .env-fil ikke funnet."
  echo "Kopier .env.example til .env og legg inn ANTHROPIC_API_KEY"
  exit 1
fi

if [ ! -d venv ]; then
  echo "Oppretter virtuelt miljø..."
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
else
  source venv/bin/activate
fi

echo ""
echo "XDi starter på http://localhost:8001"
echo "Dokumentasjon: http://localhost:8001/docs"
echo "Trykk Ctrl+C for å stoppe"
echo ""

python main.py
