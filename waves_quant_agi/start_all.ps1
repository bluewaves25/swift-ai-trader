# === START Redis Server ===
Start-Process -NoNewWindow -FilePath "C:\RedisSafe\Redis\redis-server.exe" -ArgumentList "C:\Program Files\Redis\redis.windows.conf"
Start-Sleep -Seconds 1

# === START AGI Engine (Python 3.10 env_310) ===
Start-Process -NoNewWindow -WorkingDirectory "$PSScriptRoot" -FilePath "powershell.exe" -ArgumentList @"
-Command "& {
    & '$PSScriptRoot\env_310\Scripts\Activate.ps1';
    python engine/run_engine_api.py
}"
"@

# === START Main Backend (Python 3.12 env_main) ===
Start-Process -NoNewWindow -WorkingDirectory "$PSScriptRoot" -FilePath "powershell.exe" -ArgumentList @"
-Command "& {
    & '$PSScriptRoot\env_main\Scripts\Activate.ps1';
    $env:PYTHONPATH = "$PSScriptRoot";
    uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
}"
"@

# === WAIT A BIT THEN SEND TEST PAYLOAD (Python 3.10) ===
Start-Sleep -Seconds 4
Start-Process -NoNewWindow -WorkingDirectory "$PSScriptRoot" -FilePath "powershell.exe" -ArgumentList @"
-Command "& {
    & '$PSScriptRoot\env_310\Scripts\Activate.ps1';
    python -c \"import redis, json; from datetime import datetime; r=redis.Redis(host='localhost', port=6379, decode_responses=True); r.lpush('market-data', json.dumps([{'timestamp': datetime.now().isoformat(), 'symbol': 'AAPL', 'open': 150.0, 'high': 155.0, 'low': 149.0, 'close': 154.0, 'volume': 1000000}]))\"
}"
"@
