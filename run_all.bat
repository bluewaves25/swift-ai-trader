@echo off
title  Swift AI Trader Boot
setlocal

REM ----- Activate AI ENV (Python 3.10.3) and run PyTorch AI training
start " Train Model" cmd /k "call \"C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\ai-env\Scripts\activate.bat\" && set PYTHONPATH=\"C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\backend\" && cd \"C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\backend\" && python -c \"from dotenv import load_dotenv; load_dotenv()\" && python strategy_core\train_trade_model.py"

REM ----- Run AI Scheduler (Re-trains every X days)
start " Scheduler" cmd /k "call \"C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\ai-env\Scripts\activate.bat\" && set PYTHONPATH=\"C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\backend\" && cd \"C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\backend\" && python -c \"from dotenv import load_dotenv; load_dotenv()\" && python strategy_core\scheduler.py"

REM ----- Activate Main VENV (Python 3.13.3) and run FastAPI Backend
start " FastAPI Server" cmd /k "call \"C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\venv\Scripts\activate.bat\" && set PYTHONPATH=\"C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\backend\" && cd \"C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\backend\" && \"C:\Users\BLUE WAVES\AppData\Local\Programs\Python\Python313\python.exe\" -m uvicorn src.server:app --reload --host 0.0.0.0 --port 3000"

exit
