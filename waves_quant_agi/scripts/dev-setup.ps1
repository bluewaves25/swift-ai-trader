# Waves Quant AGI - Development Setup Script for Windows
# This script sets up the development environment using Podman

param(
    [string]$Environment = "development"
)

Write-Host "🚀 Setting up Waves Quant AGI Development Environment with Podman" -ForegroundColor Green

# Check if podman is installed
try {
    $null = Get-Command podman -ErrorAction Stop
    Write-Host "✅ Podman is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Podman is not installed. Please install Podman first." -ForegroundColor Red
    Write-Host "   Visit: https://podman.io/getting-started/installation" -ForegroundColor Yellow
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

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Blue
$directories = @("logs", "models", "monitoring", "nginx/conf.d", "ssl", "init-db")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    }
}

# Create monitoring configuration
Write-Host "📊 Setting up monitoring configuration..." -ForegroundColor Blue
$prometheusConfig = @'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend-main'
    static_configs:
      - targets: ['backend-main:8000']
    metrics_path: '/metrics'

  - job_name: 'backend-ml'
    static_configs:
      - targets: ['backend-ml:8001']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
'@

Set-Content -Path "monitoring/prometheus.yml" -Value $prometheusConfig

# Create nginx configuration
Write-Host "🌐 Setting up nginx configuration..." -ForegroundColor Blue
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

    server {
        listen 80;
        server_name localhost;

        # Main Backend API
        location /api/v1/ {
            proxy_pass http://backend-main;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # ML Backend API
        location /api/v1/ml/ {
            proxy_pass http://backend-ml;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health checks
        location /health {
            proxy_pass http://backend-main;
        }

        location /ml/health {
            proxy_pass http://backend-ml;
        }
    }
}
'@

Set-Content -Path "nginx/nginx.conf" -Value $nginxConfig

# Create database initialization script
Write-Host "🗄️ Setting up database initialization..." -ForegroundColor Blue
$dbInitScript = @'
-- Initialize Waves Quant AGI Database
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- Create tables for trading data
CREATE TABLE IF NOT EXISTS market_data (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    open DECIMAL(20,8),
    high DECIMAL(20,8),
    low DECIMAL(20,8),
    close DECIMAL(20,8),
    volume DECIMAL(20,8)
);

-- Create hypertable for time-series data
SELECT create_hypertable('market_data', 'time', if_not_exists => TRUE);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data (symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_time ON market_data (time DESC);

-- Create trading signals table
CREATE TABLE IF NOT EXISTS trading_signals (
    id SERIAL PRIMARY KEY,
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    signal_type VARCHAR(10) NOT NULL, -- 'BUY', 'SELL', 'HOLD'
    confidence DECIMAL(5,4),
    model_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create user accounts table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create API keys table
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    key_name VARCHAR(100) NOT NULL,
    api_key VARCHAR(255) UNIQUE NOT NULL,
    permissions JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_used TIMESTAMPTZ
);

-- Insert sample data
INSERT INTO users (email, password_hash) VALUES 
('admin@wavesquant.com', 'sample_hash_here')
ON CONFLICT (email) DO NOTHING;
'@

Set-Content -Path "init-db/01-init.sql" -Value $dbInitScript

# Create development environment file
Write-Host "⚙️ Creating environment configuration..." -ForegroundColor Blue
$envConfig = @'
# Development Environment Configuration
ENVIRONMENT=development
DEBUG=true

# Database Configuration
DATABASE_URL=postgresql://waves:waves123@localhost:5432/waves_db
POSTGRES_DB=waves_db
POSTGRES_USER=waves
POSTGRES_PASSWORD=waves123

# Redis Configuration
REDIS_URL=redis://localhost:6379

# RabbitMQ Configuration
RABBITMQ_URL=amqp://guest:guest@localhost:5672

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ML_API_PORT=8001

# Security
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production

# External APIs
STRIPE_SECRET_KEY=your-stripe-secret-key
COINBASE_API_KEY=your-coinbase-api-key
SENDGRID_API_KEY=your-sendgrid-api-key
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
'@

Set-Content -Path ".env.development" -Value $envConfig

Write-Host "✅ Development environment setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Review and update .env.development with your API keys" -ForegroundColor White
Write-Host "2. Run: podman-compose up -d" -ForegroundColor White
Write-Host "3. Access services:" -ForegroundColor White
Write-Host "   - Main Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   - ML Backend: http://localhost:8001" -ForegroundColor Cyan
Write-Host "   - Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor Cyan
Write-Host "   - Prometheus: http://localhost:9090" -ForegroundColor Cyan
Write-Host "   - RabbitMQ: http://localhost:15672 (guest/guest)" -ForegroundColor Cyan
Write-Host "   - PostgreSQL: localhost:5432" -ForegroundColor Cyan
Write-Host ""
Write-Host "🛠️ Useful commands:" -ForegroundColor Yellow
Write-Host "  - Start services: podman-compose up -d" -ForegroundColor White
Write-Host "  - Stop services: podman-compose down" -ForegroundColor White
Write-Host "  - View logs: podman-compose logs -f" -ForegroundColor White
Write-Host "  - Rebuild: podman-compose up -d --build" -ForegroundColor White 