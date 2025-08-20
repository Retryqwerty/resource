#!/usr/bin/env bash
set -e
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
exec uvicorn main:app --host 0.0.0.0 --port 8000
