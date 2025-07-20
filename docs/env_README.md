# Environment Setup Guide

This project uses two separate Python environments to ensure compatibility and stability:

- **env_main** (Python 3.12): For backend-main (API)
- **env_310** (Python 3.10): For backend-ml (AI/ML engine)

## Communication
- Both services communicate via Redis (ensure Redis is running at C:\RedisSafe\Redis)

## Setup Instructions

1. **Create both virtual environments** (if not already present):
   - Python 3.12 for env_main
   - Python 3.10 for env_310

2. **Install requirements for each environment:**

   ### For backend-main (env_main)
   ```powershell
   .\env_main\Scripts\activate
   pip install -r backend-main/requirements.txt
   deactivate
   ```

   ### For backend-ml (env_310)
   ```powershell
   .\env_310\Scripts\activate
   pip install -r backend-ml/requirements.txt
   deactivate
   ```

3. **To set up both environments automatically, run:**
   ```powershell
   .\scripts\dev-setup.ps1
   ```

4. **To start all backend services, run (from the project root):**
   ```powershell
   .\waves_quant_agi\scripts\run-all.ps1
   ```
   This will launch both backends using `python -m` to ensure all imports work correctly.

5. **Manual start (from the project root):**
   - For backend-main:
     ```powershell
     .\waves_quant_agi\env_main\Scripts\activate
     python -m waves_quant_agi.backend-main.app
     ```
   - For backend-ml:
     ```powershell
     .\waves_quant_agi\env_310\Scripts\activate
     python -m waves_quant_agi.backend-ml.app
     ```

## Notes
- Ensure Redis is running before starting backend services.
- Both environments must have all dependencies installed for their respective services to work.
- If you add new dependencies, update the appropriate requirements file and re-run the setup.
- Always run backend services from the project root using `python -m` to avoid import errors. 