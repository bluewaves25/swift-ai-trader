# Waves Quant AGI - Production Deployment Script for Windows
# This script deploys the application using Podman

param(
    [string]$Environment = "production"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Deploying Waves Quant AGI to $Environment environment" -ForegroundColor Green

# Check if podman is installed
try {
    $null = Get-Command podman -ErrorAction Stop
    Write-Host "✅ Podman is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Podman is not installed. Please install Podman first." -ForegroundColor Red
    exit 1
}

# Check if podman-compose is installed
try {
    $null = Get-Command podman-compose -ErrorAction Stop
    Write-Host "✅ podman-compose is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ podman-compose is not installed. Installing..." -ForegroundColor Yellow
    pip install podman-compose
}

# Load environment variables
$envFile = ".env.$Environment"
if (Test-Path $envFile) {
    Write-Host "📋 Loading environment variables from $envFile" -ForegroundColor Blue
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
} else {
    Write-Host "⚠️  No $envFile file found, using defaults" -ForegroundColor Yellow
}

# Create production directories
Write-Host "📁 Creating production directories..." -ForegroundColor Blue
$directories = @("logs", "models", "ssl", "monitoring")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    }
}

# Generate SSL certificates for production (self-signed for demo)
if (!(Test-Path "ssl/cert.pem")) {
    Write-Host "🔐 Generating SSL certificates..." -ForegroundColor Blue
    if (!(Test-Path "ssl")) {
        New-Item -ItemType Directory -Path "ssl" -Force | Out-Null
    }
    
    # Check if OpenSSL is available
    try {
        $null = Get-Command openssl -ErrorAction Stop
        & openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=WavesQuant/CN=localhost"
        Write-Host "✅ SSL certificates generated" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  OpenSSL not found, skipping SSL certificate generation" -ForegroundColor Yellow
        Write-Host "   You can generate certificates manually or install OpenSSL" -ForegroundColor Yellow
    }
}

# Create production nginx configuration
Write-Host "🌐 Creating production nginx configuration..." -ForegroundColor Blue
$nginxConfig = @'
events {
    worker_connections 1024;
}

http {
    upstream backend-main {
        server backend-main:8000;
    }

    upstream backend-ml {
        server backend-ml:8001;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    server {
        listen 80;
        server_name _;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Main Backend API
        location /api/v1/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend-main;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # ML Backend API
        location /api/v1/ml/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend-ml;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }

        # Health checks
        location /health {
            proxy_pass http://backend-main;
        }

        location /ml/health {
            proxy_pass http://backend-ml;
        }

        # Monitoring endpoints (protected)
        location /monitoring/ {
            auth_basic "Monitoring";
            auth_basic_user_file /etc/nginx/.htpasswd;
            proxy_pass http://grafana:3000/;
        }
    }
}
'@

Set-Content -Path "nginx/nginx.conf" -Value $nginxConfig

# Create monitoring configuration for production
Write-Host "📊 Setting up production monitoring..." -ForegroundColor Blue
$prometheusConfig = @'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'backend-main'
    static_configs:
      - targets: ['backend-main:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'backend-ml'
    static_configs:
      - targets: ['backend-ml:8001']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'rabbitmq'
    static_configs:
      - targets: ['rabbitmq:15672']
    metrics_path: '/metrics'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          # - alertmanager:9093
'@

Set-Content -Path "monitoring/prometheus.yml" -Value $prometheusConfig

# Stop existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Blue
try {
    & podman-compose -f podman-compose.yml down
    Write-Host "✅ Existing containers stopped" -ForegroundColor Green
} catch {
    Write-Host "⚠️  No existing containers to stop" -ForegroundColor Yellow
}

# Remove old images
Write-Host "🧹 Cleaning up old images..." -ForegroundColor Blue
try {
    & podman image prune -f
    Write-Host "✅ Old images cleaned up" -ForegroundColor Green
} catch {
    Write-Host "⚠️  No old images to clean up" -ForegroundColor Yellow
}

# Build and start services
Write-Host "🔨 Building and starting services..." -ForegroundColor Blue
& podman-compose -f podman-compose.yml up -d --build

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Blue
Start-Sleep -Seconds 30

# Check service health
Write-Host "🏥 Checking service health..." -ForegroundColor Blue
$services = @("backend-main", "backend-ml", "postgres", "redis", "rabbitmq")
foreach ($service in $services) {
    Write-Host "Checking $service..." -ForegroundColor Yellow
    $status = & podman-compose -f podman-compose.yml ps | Select-String "$service.*Up"
    if ($status) {
        Write-Host "✅ $service is running" -ForegroundColor Green
    } else {
        Write-Host "❌ $service failed to start" -ForegroundColor Red
        Write-Host "Logs for $service:" -ForegroundColor Red
        & podman-compose -f podman-compose.yml logs $service
        exit 1
    }
}

# Test API endpoints
Write-Host "🧪 Testing API endpoints..." -ForegroundColor Blue
Start-Sleep -Seconds 10

# Test main backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Main backend is responding" -ForegroundColor Green
    } else {
        Write-Host "❌ Main backend is not responding" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Main backend is not responding" -ForegroundColor Red
}

# Test ML backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ ML backend is responding" -ForegroundColor Green
    } else {
        Write-Host "❌ ML backend is not responding" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ ML backend is not responding" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Service URLs:" -ForegroundColor Yellow
Write-Host "  - Main Backend: https://localhost/api/v1/" -ForegroundColor Cyan
Write-Host "  - ML Backend: https://localhost/api/v1/ml/" -ForegroundColor Cyan
Write-Host "  - Grafana: https://localhost/monitoring/ (admin/admin)" -ForegroundColor Cyan
Write-Host "  - Prometheus: http://localhost:9090" -ForegroundColor Cyan
Write-Host "  - RabbitMQ: http://localhost:15672 (guest/guest)" -ForegroundColor Cyan
Write-Host ""
Write-Host "🛠️ Useful commands:" -ForegroundColor Yellow
Write-Host "  - View logs: podman-compose -f podman-compose.yml logs -f" -ForegroundColor White
Write-Host "  - Stop services: podman-compose -f podman-compose.yml down" -ForegroundColor White
Write-Host "  - Restart: podman-compose -f podman-compose.yml restart" -ForegroundColor White
Write-Host "  - Update: .\scripts\deploy.ps1 $Environment" -ForegroundColor White 