# 🚀 ML Hackathon Agent Suite

A collection of specialized AI agents designed for 32-hour ML hackathons.

## Agent Roster

| Agent | Slash Command | Purpose |
|-------|---------------|---------|
| **Data Analyst** | `/data-analyst` | EDA, data cleaning, visualization |
| **Feature Engineer** | `/feature-engineer` | Feature creation & selection |
| **Model Trainer** | `/model-trainer` | Model training & hyperparameter tuning |
| **Ensemble Master** | `/ensemble-master` | Model blending & stacking |
| **API Developer** | `/api-developer` | FastAPI/Go backend endpoints |
| **Frontend Developer** | `/frontend-developer` | React dashboard & UI |
| **DevOps Engineer** | `/devops` | Docker, CI/CD, deployment |
| **Researcher** | `/researcher` | Papers, techniques, best practices |
| **Debugger** | `/debugger` | Error diagnosis & optimization |
| **Documentation Writer** | `/docs` | README, presentation, submission |

## Shared Rules

All agents follow these conventions:

1. **Experiment Tracking**: Log all experiments to `experiments/` directory
2. **Code Style**: Use type hints, docstrings, and clear naming
3. **Git**: Create meaningful commits with conventional commit messages
4. **Virtual Env**: Use `venv` or `conda` for Python dependencies
5. **Logging**: Use structured logging, not print statements

## Quick Start

1. Start with `/researcher` to understand the problem domain
2. Use `/data-analyst` for initial EDA
3. Parallel work: `/feature-engineer` + `/model-trainer`
4. Use `/ensemble-master` for final model
5. Deploy with `/api-developer` → `/frontend-developer` → `/devops`

## Directory Structure

```
project/
├── data/
│   ├── raw/           # Original datasets
│   ├── processed/     # Cleaned data
│   └── features/      # Engineered features
├── models/
│   ├── checkpoints/   # Model checkpoints
│   └── final/         # Final submission models
├── notebooks/         # Jupyter notebooks for EDA
├── src/
│   ├── data/          # Data processing scripts
│   ├── features/      # Feature engineering
│   ├── models/        # Model training code
│   └── api/           # API endpoints
├── frontend/          # React frontend
├── experiments/       # Experiment logs
├── docker/            # Docker files
└── docs/              # Documentation
```

## Hackathon Timeline (32 hours / 8 hacks)

| Hack | Hours | Focus |
|------|-------|-------|
| 1 | 0-4 | Problem understanding, EDA, baseline |
| 2 | 4-8 | Feature engineering v1 |
| 3 | 8-12 | Model experimentation |
| 4 | 12-16 | Advanced features + tuning |
| 5 | 16-20 | Ensemble building |
| 6 | 20-24 | API development |
| 7 | 24-28 | Frontend + integration |
| 8 | 28-32 | Polish, docs, submission |
