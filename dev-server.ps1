# Development Server Script for Waves Quant Engine
# This script starts the development server with proper SPA routing

Write-Host "🚀 Starting development server..." -ForegroundColor Green

# Check if Node.js is installed
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Node.js is not installed. Please install Node.js first." -ForegroundColor Red
    exit 1
}

# Check if npm is installed
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "❌ npm is not installed. Please install npm first." -ForegroundColor Red
    exit 1
}

# Install dependencies if node_modules doesn't exist
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Dependencies ready" -ForegroundColor Green

# Start the development server
Write-Host "🌐 Starting Vite development server..." -ForegroundColor Yellow
Write-Host "📱 Server will be available at: http://localhost:5173" -ForegroundColor Cyan
Write-Host "🔧 SPA routing is configured for direct URL access" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "- Try visiting http://localhost:5173/about directly" -ForegroundColor White
Write-Host "- Try visiting http://localhost:5173/contact directly" -ForegroundColor White
Write-Host "- Try visiting http://localhost:5173/terms directly" -ForegroundColor White
Write-Host "- All routes should work with direct URL access now!" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  No .env file found!" -ForegroundColor Yellow
    Write-Host "Please run .\setup-env.ps1 first to configure Supabase" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or create a .env file manually with:" -ForegroundColor Cyan
    Write-Host "VITE_SUPABASE_URL=https://your-project.supabase.co" -ForegroundColor White
    Write-Host "VITE_SUPABASE_ANON_KEY=your-anon-key" -ForegroundColor White
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

# Start the dev server
npm run dev 