#!/bin/bash
set -e
python3 -m src.embed_and_store
exec python3 -m uvicorn api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
