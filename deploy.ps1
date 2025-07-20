# Deployment Script for Waves Quant Engine
# This script builds the frontend and prepares for production deployment

Write-Host "🚀 Starting deployment process..." -ForegroundColor Green

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

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Build the React app
Write-Host "🔨 Building React app..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}

# Check if build was successful
if (-not (Test-Path "dist")) {
    Write-Host "❌ Build directory 'dist' not found" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Build completed successfully!" -ForegroundColor Green

# Copy deployment files to dist
Write-Host "📁 Copying deployment files..." -ForegroundColor Yellow

# Copy _redirects for Netlify/Vercel
if (Test-Path "public/_redirects") {
    Copy-Item "public/_redirects" "dist/_redirects" -Force
    Write-Host "✅ Copied _redirects file" -ForegroundColor Green
}

# Copy .htaccess for Apache
if (Test-Path "public/.htaccess") {
    Copy-Item "public/.htaccess" "dist/.htaccess" -Force
    Write-Host "✅ Copied .htaccess file" -ForegroundColor Green
}

# Create nginx.conf in dist for Nginx deployment
if (Test-Path "nginx.conf") {
    Copy-Item "nginx.conf" "dist/nginx.conf" -Force
    Write-Host "✅ Copied nginx.conf file" -ForegroundColor Green
}

Write-Host "🎉 Deployment preparation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. For Netlify/Vercel: Upload the 'dist' folder" -ForegroundColor White
Write-Host "2. For Apache: Upload 'dist' contents to your web server" -ForegroundColor White
Write-Host "3. For Nginx: Copy 'dist/nginx.conf' to your server and update paths" -ForegroundColor White
Write-Host "4. For Python backend: The backend will serve the React app automatically" -ForegroundColor White
Write-Host ""
Write-Host "📁 Build output: dist/" -ForegroundColor Cyan 