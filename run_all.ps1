# Swift AI Trader Boot
$ErrorActionPreference = "Stop"

# Activate AI ENV (Python 3.10.3) and run PyTorch AI training
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& 'C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\ai-env\Scripts\Activate.ps1'; `$env:PYTHONPATH='C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader'; Set-Location 'C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\backend'; python strategy_core\train_trade_model.py" -WindowStyle Normal

# Run AI Scheduler (Re-trains every X days)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& 'C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\ai-env\Scripts\Activate.ps1'; `$env:PYTHONPATH='C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader'; Set-Location 'C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\backend'; python strategy_core\scheduler.py" -WindowStyle Normal

# Run System Status Updater (Fetches system table status for Redis)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& 'C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\ai-env\Scripts\Activate.ps1'; `$env:PYTHONPATH='C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader'; Set-Location 'C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\backend'; python strategy_core\system_status.py" -WindowStyle Normal

# Activate Main VENV (Python 3.13.3) and run FastAPI Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& 'C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\venv\Scripts\Activate.ps1'; `$env:PYTHONPATH='C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader'; Set-Location 'C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\backend'; python -m uvicorn src.server:app --reload --host 0.0.0.0 --port 3000" -WindowStyle Normal
