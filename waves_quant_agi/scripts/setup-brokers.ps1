# Setup Broker Environment Variables
# This script helps configure broker credentials for real trading

Write-Host "=== Waves Quant AGI - Broker Setup ===" -ForegroundColor Green
Write-Host ""

# Binance Configuration
Write-Host "=== Binance Configuration ===" -ForegroundColor Yellow
$binance_api_key = Read-Host "Enter your Binance API Key (or press Enter to skip)"
$binance_api_secret = Read-Host "Enter your Binance API Secret (or press Enter to skip)"

if ($binance_api_key -and $binance_api_secret) {
    [Environment]::SetEnvironmentVariable("BINANCE_API_KEY", $binance_api_key, "User")
    [Environment]::SetEnvironmentVariable("BINANCE_API_SECRET", $binance_api_secret, "User")
    Write-Host "✓ Binance credentials configured" -ForegroundColor Green
} else {
    Write-Host "⚠ Binance credentials not configured - will use mock data" -ForegroundColor Yellow
}

Write-Host ""

# MT5/Exness Configuration
Write-Host "=== MT5/Exness Configuration ===" -ForegroundColor Yellow
$mt5_login = Read-Host "Enter your MT5 Login (or press Enter to skip)"
$mt5_password = Read-Host "Enter your MT5 Password (or press Enter to skip)"
$mt5_server = Read-Host "Enter your MT5 Server (default: Exness-MT5)"

if ($mt5_login -and $mt5_password) {
    [Environment]::SetEnvironmentVariable("MT5_LOGIN", $mt5_login, "User")
    [Environment]::SetEnvironmentVariable("MT5_PASSWORD", $mt5_password, "User")
    [Environment]::SetEnvironmentVariable("MT5_SERVER", $mt5_server, "User")
    Write-Host "✓ MT5 credentials configured" -ForegroundColor Green
} else {
    Write-Host "⚠ MT5 credentials not configured - will use mock data" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host "Restart your terminal/IDE for environment variables to take effect" -ForegroundColor Cyan
Write-Host ""

# Instructions
Write-Host "=== Next Steps ===" -ForegroundColor Blue
Write-Host "1. Restart your terminal/IDE" -ForegroundColor White
Write-Host "2. Run the backend: .\run-all.ps1" -ForegroundColor White
Write-Host "3. The engine will now use real market data if credentials are configured" -ForegroundColor White
Write-Host "4. Check the LiveSignals component for real trading signals" -ForegroundColor White
Write-Host "" 