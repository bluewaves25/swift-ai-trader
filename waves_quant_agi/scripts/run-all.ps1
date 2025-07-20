# Run All Backend Services for Swift AI Trader
# This script starts Redis, backend-main (API), and backend-ml (ML engine)
# Ensure you have the correct Python environments set up as per project instructions

# Start Redis server
Write-Host "Starting Redis server..."
Start-Process -NoNewWindow -FilePath "C:\RedisSafe\Redis\redis-server.exe" -RedirectStandardOutput "redis.log" -RedirectStandardError "redis.err.log"
Start-Sleep -Seconds 2

# Get project root
$projectRoot = Resolve-Path "$PSScriptRoot\..\.."

# Start backend-main (API) in env_main using python -m, log output
Write-Host "Starting backend-main (API) in env_main..."
Start-Process powershell -WorkingDirectory $projectRoot -ArgumentList '-NoExit', '-Command', '$env:DISCOVER_STRATEGIES="false"; .\waves_quant_agi\env_main\Scripts\activate; python -m waves_quant_agi.backend-main.app *>> backend-main.log' -WindowStyle Normal
Start-Sleep -Seconds 2

# Start backend-ml (ML engine) in env_310 using python -m, log output
Write-Host "Starting backend-ml (ML engine) in env_310..."
Start-Process powershell -WorkingDirectory $projectRoot -ArgumentList '-NoExit', '-Command', '$env:DISCOVER_STRATEGIES="true"; .\waves_quant_agi\env_310\Scripts\activate; python -m waves_quant_agi.backend-ml.app *>> backend-ml.log' -WindowStyle Normal

# Optionally, start additional engine workers for scaling
# Write-Host "Starting additional trading engine worker..."
# Start-Process powershell -WorkingDirectory $projectRoot -ArgumentList '-NoExit', '-Command', 'Set-Location $projectRoot; $env:PYTHONPATH=$projectRoot; $env:DISCOVER_STRATEGIES="true"; .\waves_quant_agi\env_310\Scripts\activate; python waves_quant_agi/engine/run_engine_api.py *>> trading-engine.log' -WindowStyle Normal

Write-Host "All backend services started. Logs: redis.log, backend-main.log, backend-ml.log, trading-engine.log" 