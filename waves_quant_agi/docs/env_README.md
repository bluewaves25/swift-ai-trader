# Environment Setup Guide

This project uses two separate Python environments to ensure compatibility and stability:

- **env_main** (Python 3.12): For backend-main (API, billing, admin, investor, owner)
- **env_310** (Python 3.10): For backend-ml (AI/ML engine, strategy execution)

## Required Environment Variables
- See `.env.example` for all required variables (Paystack, DB, Redis, etc.)
- Place `.env` in both backend and frontend as needed

## Setup Instructions

1. **Create both virtual environments** (if not already present):
   - Python 3.12 for env_main
   - Python 3.10 for env_310

2. **Install requirements for each environment:**
   ```bash
   # For backend-main (env_main)
   .\env_main\Scripts\activate
   pip install -r backend-main/requirements.txt
   deactivate

   # For backend-ml (env_310)
   .\env_310\Scripts\activate
   pip install -r backend-ml/requirements.txt
   deactivate
   ```

3. **To set up both environments automatically, run:**
   ```bash
   .\scripts\dev-setup.ps1
   ```

4. **To start all backend services, run:**
   ```bash
   .\scripts\run-all.ps1
   ```

## Notes
- Ensure Redis is running before starting backend services.
- Both environments must have all dependencies installed for their respective services to work.
- If you add new dependencies, update the appropriate requirements file and re-run the setup.
- Always run backend services from the project root using `python -m` to avoid import errors.
