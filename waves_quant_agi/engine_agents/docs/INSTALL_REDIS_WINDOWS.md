# 🚀 Installing Redis on Windows for Trading Engine

## Option 1: Using Chocolatey (Recommended)

### 1. Install Chocolatey (if not already installed)
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

### 2. Install Redis
```powershell
# Run as Administrator
choco install redis-64
```

### 3. Start Redis Service
```powershell
# Start Redis service
net start redis

# Or start manually
redis-server
```

## Option 2: Manual Installation

### 1. Download Redis for Windows
- Go to: https://github.com/microsoftarchive/redis/releases
- Download the latest release (e.g., `Redis-x64-3.0.504.msi`)

### 2. Install Redis
- Run the downloaded MSI file
- Follow the installation wizard
- Make sure to check "Add to PATH" during installation

### 3. Start Redis
```powershell
# Start Redis service
net start redis

# Or start manually
redis-server
```

## Option 3: Using Docker (Alternative)

### 1. Install Docker Desktop
- Download from: https://www.docker.com/products/docker-desktop
- Install and start Docker Desktop

### 2. Run Redis in Docker
```powershell
docker run -d --name redis -p 6379:6379 redis:latest
```

## Option 4: Mock Redis for Testing

If you want to test the trading engine without installing Redis, you can use a mock Redis server:

```python
# Create a file called mock_redis.py
import threading
import time
import json
from collections import defaultdict

class MockRedis:
    def __init__(self):
        self.data = defaultdict(str)
        self.pubsub = {}
        self.lists = defaultdict(list)
        
    def ping(self):
        return True
        
    def set(self, key, value):
        self.data[key] = value
        return True
        
    def get(self, key):
        return self.data.get(key)
        
    def publish(self, channel, message):
        if channel in self.pubsub:
            self.pubsub[channel].append(message)
        return 1
        
    def keys(self, pattern):
        return [k for k in self.data.keys() if pattern.replace('*', '') in k]

# Usage in your code:
# import mock_redis
# redis_client = mock_redis.MockRedis()
```

## Testing Redis Installation

After installing Redis, test it:

```powershell
# Test Redis connection
redis-cli ping

# Should return: PONG
```

## Quick Start for Trading Engine

Once Redis is installed and running:

```powershell
# Navigate to the engine_agents directory
cd C:\Users\BLUE WAVES\Documents\GitHub\swift-ai-trader\waves_quant_agi\engine_agents

# Start the trading engine
python pipeline_runner.py
```

## Troubleshooting

### Redis Connection Issues
```powershell
# Check if Redis is running
netstat -an | findstr 6379

# Restart Redis service
net stop redis
net start redis
```

### Port Already in Use
If port 6379 is already in use:
```powershell
# Find what's using the port
netstat -ano | findstr 6379

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

## Alternative: Use Redis Cloud (Free Tier)

If you don't want to install Redis locally:

1. Go to https://redis.com/try-free/
2. Create a free account
3. Get your Redis connection details
4. Update the configuration in `pipeline_runner.py`:

```python
config = {
    "redis_host": "your-redis-host.redis.cloud",
    "redis_port": 6379,
    "redis_password": "your-redis-password"
}
```

## Next Steps

Once Redis is installed and running:

1. **Start the Trading Engine:**
   ```powershell
   python pipeline_runner.py
   ```

2. **Monitor Pipeline:**
   ```powershell
   # In another terminal
   python test_pipeline.py
   ```

3. **Check Status:**
   ```powershell
   python test_pipeline.py --status
   ```

## Recommended Setup

For development and testing, I recommend:

1. **Install Redis using Chocolatey** (Option 1)
2. **Use the default configuration** (localhost:6379)
3. **Start Redis as a Windows service** for automatic startup

This will give you a stable Redis installation that starts automatically with Windows.
