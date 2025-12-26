#!/bin/bash
echo "🛠️  Starting Clinical Copilot (Developer Mode)..."

# Trap Ctrl+C to kill all background processes
trap "kill 0" EXIT

# 1. Start ML API
echo "Starting ML API (Port 8000)..."
(cd src/api/ml_api && ../../../venv/bin/uvicorn main:app --reload --port 8000) &

# 2. Start Go Backend
echo "Starting Go Backend (Port 3000)..."
(cd backend && go run main.go) &

# 3. Start Frontend
echo "Starting Frontend (Port 3001)..."
(cd frontend && npm run dev -- -p 3001) &

wait
