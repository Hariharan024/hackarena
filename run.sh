#!/usr/bin/env bash
# One-command start on macOS/Linux:  ./run.sh   ->  http://localhost:8000
set -euo pipefail
cd "$(dirname "$0")"
[ -d backend/.venv ] || python3 -m venv backend/.venv
backend/.venv/bin/pip install -q -r backend/requirements.txt
[ -f backend/.env ] || { cp backend/.env.example backend/.env; echo "Created backend/.env - add your GEMINI_API_KEY there (optional)."; }
(cd frontend && npm install --no-audit --no-fund && npm run build)
cd backend && exec .venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
