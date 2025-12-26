#!/bin/bash
echo "🚀 Starting Clinical Copilot (Production Mode)..."
docker-compose up -d --build
echo "✅ Services deployed!"
echo "   - Frontend: http://localhost:3001"
echo "   - Backend:  http://localhost:3000"
echo "   - ML API:   http://localhost:8000"
