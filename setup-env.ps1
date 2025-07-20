# Environment Setup Script for Waves Quant Engine
# This script helps you set up your .env file

Write-Host "🔧 Setting up environment variables..." -ForegroundColor Green

# Check if .env file exists
if (Test-Path ".env") {
    Write-Host "⚠️  .env file already exists!" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to overwrite it? (y/N)"
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "❌ Setup cancelled" -ForegroundColor Red
        exit 0
    }
}

Write-Host ""
Write-Host "📝 Please provide your Supabase credentials:" -ForegroundColor Cyan
Write-Host ""

$supabaseUrl = Read-Host "Enter your Supabase URL (e.g., https://your-project.supabase.co)"
$supabaseKey = Read-Host "Enter your Supabase Anon Key"

# Validate inputs
if (-not $supabaseUrl -or -not $supabaseKey) {
    Write-Host "❌ Both URL and Key are required!" -ForegroundColor Red
    exit 1
}

# Create .env file
$envContent = @"
# Supabase Configuration
VITE_SUPABASE_URL=$supabaseUrl
VITE_SUPABASE_ANON_KEY=$supabaseKey

# Backend API URL (if different from default)
VITE_API_URL=http://localhost:8000

# Development settings
VITE_DEV_MODE=true
"@

# Write to .env file
$envContent | Out-File -FilePath ".env" -Encoding UTF8

Write-Host ""
Write-Host "✅ .env file created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Restart your development server" -ForegroundColor White
Write-Host "2. Check the browser console for any remaining errors" -ForegroundColor White
Write-Host "3. Try navigating to /about, /contact, /terms directly" -ForegroundColor White
Write-Host ""
Write-Host "🔗 Your Supabase URL: $supabaseUrl" -ForegroundColor Gray
Write-Host "🔑 Your Supabase Key: $($supabaseKey.Substring(0, [Math]::Min(10, $supabaseKey.Length)))..." -ForegroundColor Gray 