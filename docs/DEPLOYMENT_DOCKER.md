# 🐳 Production Deployment: Docker & PostgreSQL

Clinical Copilot v3.0 supports a fully containerized deployment using Docker and Docker Compose. This architecture is designed for production reliability, utilizing a high-performance **PostgreSQL** database instead of the development-stage SQLite.

---

## 🏗️ Container Architecture

The system is decomposed into four specialized services, communicating over an internal Docker network (`healthcare-net`):

| Service | Container Name | Image/Runtime | Port | Purpose |
|---------|----------------|---------------|------|---------|
| **Frontend** | `healthcare-frontend` | Next.js (Node:20) | 3001 | Clinical Cockpit UI |
| **Backend** | `healthcare-backend` | Go 1.21 | 3000 | Orchestration & RAG |
| **ML API** | `healthcare-ml-api` | Python 3.10 | 8000 | XGBoost/RF Inference |
| **Database** | `healthcare-db` | Postgres 15 | 5432 | Persistent Storage |

---

## 🚀 Deployment Guide

### 1. Simple Startup
Use the provided automation script to build and launch all services:
```bash
bash scripts/start.sh
```

### 2. Manual Commands
If you prefer fine-grained control:
```bash
# Build and start in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

---

## 💾 Database Persistence

In production mode, the system automatically migrates from `clinical.db` (SQLite) to a persistent **PostgreSQL** volume.

- **Storage**: Data is persisted in a named Docker volume `postgres_data`.
- **Initialization**: The Go backend (`healthcare-backend`) automatically performs GORM auto-migrations on the Postgres schema upon startup.
- **Health-Checks**: The backend container waits for the Postgres health-check (`pg_isready`) before initializing to prevent connection timeouts.

---

## 📡 Environment Configuration

The `docker-compose.yml` file utilizes the `.env` file for sensitive keys. Ensure your `.env` contains:
```env
GEMINI_API_KEY=your_key_here
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=healthcare
```

---

## 🔧 Managing Services

### Scaling the ML API
To handle high clinical loads, you can scale the stateless ML inference service:
```bash
docker-compose up -d --scale ml-api=3
```

### Accessing the Database
To connect to the Postgres instance manually:
```bash
docker exec -it healthcare-db psql -U postgres -d healthcare
```

---
*Containerized for the next generation of clinical intelligence.*
