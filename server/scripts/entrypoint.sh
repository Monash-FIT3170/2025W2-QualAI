#!/usr/bin/env bash
set -e

# 1) Wait for Qdrant to accept TCP connections
echo "Waiting for Qdrant at $QDRANT_URL ..."
until curl -sf "$QDRANT_URL/collections" >/dev/null; do
  sleep 2
done
echo "Qdrant is up"

# 2) Run ingest exactly once (skip if collection already exists)
echo "Checking if collection 'test_db' exists"
if ! curl -sf "$QDRANT_URL/collections/test_db" >/dev/null ; then
  echo "Ingesting PDF into Qdrant ..."
  python /app/scripts/ingest.py
else
  echo "Collection already present; skipping ingest"
fi

# 3) Start the FastAPI server (same cmd you had before)
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
