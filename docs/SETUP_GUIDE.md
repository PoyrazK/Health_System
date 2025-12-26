# 🚀 Setup Guide - Clinical Copilot

This guide provides step-by-step instructions for setting up Clinical Copilot on your local machine.

---

## Prerequisites

### Required Software

| Software | Minimum Version | Download |
|----------|-----------------|----------|
| **Go** | 1.21+ | [go.dev](https://go.dev/dl/) |
| **Python** | 3.10+ | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 18+ | [nodejs.org](https://nodejs.org/) |
| **Git** | 2.30+ | [git-scm.com](https://git-scm.com/) |

### Verify Installation

```bash
# Check versions
go version      # go version go1.21.x darwin/arm64
python3 --version  # Python 3.10.x
node --version     # v18.x.x
npm --version      # 9.x.x
```

---

## Quick Start (5 Minutes)

### 1. Clone Repository

```bash
git clone <repository-url>
cd "Healthcare System"
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# .env
GEMINI_API_KEY=your_gemini_api_key_here
```

> [!NOTE]
> Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/). The system works without it (mock LLM responses).

### 3. Start All Services

```bash
# Terminal 1: Python ML API
source venv/bin/activate
uvicorn src.api.ml_api.main:app --port 8000

# Terminal 2: Go Backend
cd backend
go run main.go

# Terminal 3: Frontend
cd frontend
npm install
npm run dev -- -p 3001
```

### 4. Access Application

Open your browser to: **http://localhost:3001**

---

## Detailed Setup

### Python Environment

#### Create Virtual Environment

```bash
# From project root
python3 -m venv venv
```

#### Activate Virtual Environment

```bash
# macOS/Linux
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat
```

#### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Required Python Packages

```
fastapi>=0.100.0
uvicorn>=0.22.0
pydantic>=2.0.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
xgboost>=2.0.0
joblib>=1.3.0
google-generativeai>=0.3.0
```

#### Verify Python Setup

```bash
python -c "import fastapi, pandas, sklearn, xgboost; print('✅ All packages installed')"
```

---

### Go Backend

#### Install Go Dependencies

```bash
cd backend
go mod download
```

#### Required Go Modules

```go
// go.mod
require (
    github.com/gofiber/fiber/v2 v2.52.0
    gorm.io/gorm v1.25.5
    gorm.io/driver/sqlite v1.5.4
)
```

#### Build and Run

```bash
# Development (with hot reload if using air)
go run main.go

# Or build binary
go build -o clinical-copilot main.go
./clinical-copilot
```

#### Verify Go Setup

```bash
curl http://localhost:3000
# Expected: 🏥 Healthcare Clinical Copilot | Phase 4 Production Ready
```

---

### Frontend Setup

#### Install Node Dependencies

```bash
cd frontend
npm install
```

#### Key Dependencies

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "tailwindcss": "^3.0.0",
    "framer-motion": "^10.0.0",
    "lucide-react": "^0.300.0"
  }
}
```

#### Run Development Server

```bash
npm run dev -- -p 3001
```

#### Build for Production

```bash
npm run build
npm start
```

---

## Service Configuration

### Port Configuration

| Service | Default Port | Environment Variable |
|---------|--------------|---------------------|
| Frontend | 3001 | `PORT` (Next.js) |
| Go Backend | 3000 | Hardcoded in `main.go` |
| ML API | 8000 | `--port` flag |

### Changing Ports

**Frontend:**
```bash
npm run dev -- -p 4000
```

**Backend (modify `main.go`):**
```go
log.Fatal(app.Listen(":8080"))
```

**ML API:**
```bash
uvicorn src.api.ml_api.main:app --port 8001
```

> [!WARNING]
> If you change the ML API port, update `ML_SERVICE_URL` in `backend/main.go`.

---

## Database Setup

### SQLite (Default)

The SQLite database is automatically created on first run:

```
backend/clinical.db
```

### Demo Data

The backend seeds demo patients on first startup:
1. **Ahmet Amca** - Emergency case (high BP, high glucose)
2. **Zeynep Hanım** - Stable case (normal vitals)

### Reset Database

```bash
# Delete and restart to regenerate
rm backend/clinical.db
cd backend && go run main.go
```

---

## Troubleshooting

### Common Issues

#### 1. Python: Module Not Found

```bash
# Error: ModuleNotFoundError: No module named 'fastapi'

# Solution: Ensure venv is activated
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Go: Package Not Found

```bash
# Error: cannot find package "github.com/gofiber/fiber/v2"

# Solution: Download dependencies
cd backend
go mod download
```

#### 3. Frontend: Port Already in Use

```bash
# Error: Port 3001 is already in use

# Solution: Use a different port
npm run dev -- -p 3002
```

#### 4. ML API: Models Not Loading

```bash
# Error: ❌ Error loading models: [Errno 2] No such file or directory

# Solution: Verify models exist
ls -la models/
# Should see: heart_model.pkl, diabetes_model.pkl, etc.
```

#### 5. LLM: No API Key

```bash
# Warning: ⚠️ GEMINI_API_KEY not found. LLM endpoint will return mock responses.

# The system will still work with mock diagnoses
# To enable real LLM: Add GEMINI_API_KEY to .env
```

#### 6. Backend: Cannot Connect to ML API

```bash
# Error: ML Service Offline (503)

# Solution: Ensure ML API is running
curl http://localhost:8000/health
# Should return: {"status": "ok", "models_loaded": [...]}
```

---

## Development Tips

### Running All Services (Script)

Create a `start-all.sh` script:

```bash
#!/bin/bash

# Start ML API
osascript -e 'tell app "Terminal" to do script "cd ~/Healthcare\ System && source venv/bin/activate && uvicorn src.api.ml_api.main:app --port 8000"'

# Start Go Backend
osascript -e 'tell app "Terminal" to do script "cd ~/Healthcare\ System/backend && go run main.go"'

# Start Frontend
osascript -e 'tell app "Terminal" to do script "cd ~/Healthcare\ System/frontend && npm run dev -- -p 3001"'

echo "✅ All services starting..."
```

### Hot Reload (Go)

Install [Air](https://github.com/cosmtrek/air) for Go hot reload:

```bash
go install github.com/cosmtrek/air@latest

# In backend directory
air
```

### Logging

All services log to stdout:
- **Go Backend:** Fiber request logger
- **ML API:** Uvicorn access logs
- **Frontend:** Next.js dev output

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ | - | Google Gemini API key |
| `PORT` | ❌ | 3001 | Frontend port |
| `NODE_ENV` | ❌ | development | Next.js environment |

### Creating `.env.example`

```bash
# .env.example (commit this, not .env)
GEMINI_API_KEY=your_api_key_here
```

---

## Verification Checklist

After setup, verify each component:

- [ ] **ML API**: `curl http://localhost:8000/health` returns `{"status": "ok"}`
- [ ] **Backend**: `curl http://localhost:3000` returns welcome message
- [ ] **Frontend**: `http://localhost:3001` loads dashboard
- [ ] **Database**: `backend/clinical.db` file exists
- [ ] **Models**: All 4 `.pkl` files in `models/`
- [ ] **Demo Data**: Two patients appear in sidebar

---

## Next Steps

1. [API Reference](./API_REFERENCE.md) - Learn the endpoints
2. [Architecture](./ARCHITECTURE.md) - Understand the system
3. [ML Models](./ML_MODELS.md) - Explore the models
4. [Approach](./approach.md) - Read the solution methodology

---

*Need help? Open an issue on the repository or contact the team.*
