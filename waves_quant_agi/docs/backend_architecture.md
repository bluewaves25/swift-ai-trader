# Backend Architecture – Waves Quant Engine

## Folder Structure

- **api/**: Entry gate; handles all requests from outside (routes, middleware)
- **backend-main/**: Main FastAPI backend (API, billing, admin, investor, owner)
- **backend-ml/**: AI/ML engine (strategy execution, analytics)
- **config/**: Settings, logging, environment variables
- **core/**: Database models, schemas, and core logic
- **docs/**: Documentation for backend, setup, and architecture
- **engine/**: Trading engine, strategies, intelligence, validation
- **requirements/**: Requirements for each Python environment
- **scripts/**: Setup, run, and deploy scripts
- **services/**: External integrations (payment, notification, portfolio, websocket)
- **shared/**: Shared settings and config
- **tests/**: Automated tests for API, engine, and services
- **utils/**: Helper files, reusable checks

## Key Files
- `app.py` (backend-main): Main FastAPI entrypoint
- `app.py` (backend-ml): ML/AI engine entrypoint
- `run_engine_api.py`: Trading engine worker (market data, strategy execution)
- `requirements.txt`: Python dependencies for each environment

## See also:
- `backend_overview.md` for backend logic
- `env_README.md` for environment setup
- Main README for full feature list