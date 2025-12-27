---
description: DevOps Engineer Agent - Docker, deployment, CI/CD, and Git Management
---

## Git Operations
### Initialization
1. Initialize git if not already: `git init`
2. Create standard `.gitignore` (ignoring `__pycache__`, `.env`, `data/`, `models/*.pkl`).
3. Initial commit.

### Routine Commit
1. Check status: `git status`
2. **Critical Step**: If adding processed data (e.g., `data/train_processed.csv`) or final models, check if they are ignored.
   - If ignored but needed: Use `git add -f <file>` (Force Add).
   - If ignored by mistake: Update `.gitignore`.
3. Add all changes: `git add .`
4. Commit with a descriptive message: `git commit -m "[Description of changes]"`

### Emergency Revert
1. View log: `git log --oneline -n 5`
2. Revert the last commit: `git revert HEAD`

## Deployment Operations
### Docker Setup
1. Analyze the `app/` and `src/` to determine dependencies.
2. Create `requirements.txt` or `pyproject.toml`.
3. Create a `Dockerfile` optimized for python (slim-buster or alpine).
4. Create `docker-compose.yml` if database/redis is needed.
5. **Verify Service Health**: `docker-compose logs --tail=50 -f [service_name]` to check for startup errors.

### Fast Docker Build (Turbo Mode)
// turbo-all
```bash
# Enable BuildKit + parallel builds (40-60% faster)
DOCKER_BUILDKIT=1 docker-compose build --parallel

# Build specific service only
DOCKER_BUILDKIT=1 docker-compose build ml-api

# Full stack up with build
DOCKER_BUILDKIT=1 docker-compose up --build -d
```

