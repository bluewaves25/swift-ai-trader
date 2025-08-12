#!/usr/bin/env python3
"""
MAIN.PY - PURE API SERVER
Beautiful FastAPI server for monitoring and controlling the trading engine.
NO engine logic, NO loops - just clean API endpoints.
"""

import os
import sys
import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import redis

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
def load_environment():
    """Load environment variables with defaults."""
    defaults = {
        "MT5_LOGIN": "248746257",
        "MT5_PASSWORD": "Stephen@55",
        "MT5_SERVER": "Exness-MT5Trial",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379"
    }
    for key, value in defaults.items():
        os.environ.setdefault(key, value)

load_environment()

# Create FastAPI app
app = FastAPI(
    title="Waves Quant AI Trading Engine API",
    description="Beautiful API for monitoring and controlling your trading engine",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state tracking
engine_state = {
    "agents_running": False,
    "trading_active": False,
    "last_startup": None,
    "redis_connected": False
}

# API Models
class TradingCommand(BaseModel):
    action: str  # start, stop, restart
    target: str  # agents, trading, system

class EngineStartup(BaseModel):
    start_agents: bool = True
    start_trading: bool = True
    redis_host: str = "localhost"
    redis_port: int = 6379

# Redis connection for monitoring
def get_redis_connection():
    """Get Redis connection for monitoring."""
    try:
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=0,
            decode_responses=True
        )
        redis_client.ping()
        engine_state["redis_connected"] = True
        return redis_client
    except:
        engine_state["redis_connected"] = False
        return None

@app.get("/")
async def root():
    """Welcome endpoint."""
    return {
        "message": "🚀 Waves Quant AI Trading Engine API",
        "version": "3.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "engine_status": "/engine/status",
            "start_engine": "/engine/start",
            "stop_engine": "/engine/stop",
            "agent_status": "/agents/status",
            "trading_status": "/trading/status"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    redis_client = get_redis_connection()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "running",
            "redis": "connected" if redis_client else "disconnected",
            "agents": "running" if engine_state["agents_running"] else "stopped",
            "trading": "active" if engine_state["trading_active"] else "inactive"
        },
        "uptime": time.time() - engine_state.get("last_startup", time.time())
    }

@app.get("/engine/status")
async def get_engine_status():
    """Get comprehensive engine status."""
    redis_client = get_redis_connection()
    
    # Get agent stats from Redis
    agent_stats = {}
    if redis_client:
        try:
            # Check for agent heartbeats
            agent_names = [
                "communication_hub", "data_feeds", "adapters", "strategy_engine",
                "risk_management", "execution", "validation", "intelligence",
                "market_conditions", "core", "fees_monitor", "failure_prevention"
            ]
            
            for agent in agent_names:
                last_heartbeat = redis_client.get(f"heartbeat:{agent}")
                agent_stats[agent] = {
                    "status": "running" if last_heartbeat else "unknown",
                    "last_seen": last_heartbeat or "never"
                }
        except Exception as e:
            agent_stats = {"error": str(e)}
    
    return {
        "engine": {
            "overall_status": "running" if engine_state["agents_running"] else "stopped",
            "agents_running": engine_state["agents_running"],
            "trading_active": engine_state["trading_active"],
            "last_startup": engine_state["last_startup"],
            "redis_connected": engine_state["redis_connected"]
        },
        "agents": agent_stats,
        "system": {
            "mt5_configured": bool(os.getenv("MT5_LOGIN")),
            "redis_host": os.getenv("REDIS_HOST"),
            "redis_port": os.getenv("REDIS_PORT")
        }
    }

@app.post("/engine/start")
async def start_engine(config: EngineStartup):
    """Start the trading engine components."""
    try:
        if config.start_agents:
            # Import and start parallel agent runner
            from engine_agents.parallel_agent_runner import start_all_agents
            await start_all_agents()
            engine_state["agents_running"] = True
        
        if config.start_trading:
            # Import and start NEW trading engine
            from engine_agents.trading_engine import TradingEngine
            trading_engine = TradingEngine()
            success = await trading_engine.start_trading_engine()
            if success:
                engine_state["trading_active"] = True
            else:
                raise Exception("Failed to start trading engine")
        
        engine_state["last_startup"] = time.time()
        
        return {
            "status": "success",
            "message": "Trading engine started successfully",
            "components": {
                "agents": "started" if config.start_agents else "skipped",
                "trading": "started" if config.start_trading else "skipped"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start engine: {str(e)}")

@app.post("/engine/stop")
async def stop_engine():
    """Stop the trading engine."""
    try:
        # Stop NEW trading engine
        if engine_state["trading_active"]:
            from engine_agents.trading_engine import TradingEngine
            trading_engine = TradingEngine()
            await trading_engine.stop_trading_engine()
            engine_state["trading_active"] = False
        
        # Stop agents
        if engine_state["agents_running"]:
            from engine_agents.parallel_agent_runner import stop_all_agents
            await stop_all_agents()
            engine_state["agents_running"] = False
        
        return {
            "status": "success",
            "message": "Trading engine stopped successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop engine: {str(e)}")

@app.post("/trading/command")
async def execute_trading_command(command: TradingCommand):
    """Execute trading commands."""
    redis_client = get_redis_connection()
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis not available")
    
    try:
        # Send command to trading cycle via Redis
        command_data = {
            "action": command.action,
            "target": command.target,
            "timestamp": time.time()
        }
        redis_client.lpush("trading_commands", json.dumps(command_data))
        
        return {
            "status": "success",
            "message": f"Command '{command.action}' sent to {command.target}",
            "command": command_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute command: {str(e)}")

@app.get("/trading/status")
async def get_trading_status():
    """Get current trading status."""
    redis_client = get_redis_connection()
    if not redis_client:
        return {"error": "Redis not available"}
    
    try:
        # Get trading stats from Redis
        stats = redis_client.hgetall("trading_stats")
        positions = redis_client.lrange("active_positions", 0, -1)
        recent_trades = redis_client.lrange("recent_trades", 0, 9)  # Last 10 trades
        
        return {
            "trading_active": engine_state["trading_active"],
            "statistics": stats or {},
            "active_positions": len(positions),
            "recent_trades": len(recent_trades),
            "last_update": time.time()
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/agents/status")
async def get_agents_status():
    """Get detailed agent status."""
    redis_client = get_redis_connection()
    if not redis_client:
        return {"error": "Redis not available"}
    
    try:
        agent_details = {}
        agent_names = [
            "communication_hub", "data_feeds", "adapters", "strategy_engine",
            "risk_management", "execution", "validation", "intelligence",
            "market_conditions", "core", "fees_monitor", "failure_prevention"
        ]
        
        for agent in agent_names:
            stats = redis_client.hgetall(f"agent_stats:{agent}")
            logs = redis_client.lrange(f"agent_logs:{agent}", 0, 4)  # Last 5 logs
            
            agent_details[agent] = {
                "stats": stats or {},
                "recent_logs": logs,
                "status": "running" if stats else "unknown"
            }
        
        return {
            "total_agents": len(agent_names),
            "agents_running": engine_state["agents_running"],
            "details": agent_details
        }
        
    except Exception as e:
        return {"error": str(e)}

@app.get("/system/logs")
async def get_system_logs():
    """Get recent system logs."""
    redis_client = get_redis_connection()
    if not redis_client:
        return {"error": "Redis not available"}
    
    try:
        system_logs = redis_client.lrange("system_logs", 0, 49)  # Last 50 logs
        error_logs = redis_client.lrange("error_logs", 0, 19)   # Last 20 errors
        
        return {
            "system_logs": system_logs,
            "error_logs": error_logs,
            "timestamp": time.time()
        }
        
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    
    print("🌐 Starting Beautiful Waves Quant Trading API...")
    print("📊 Pure API server - no engine logic here!")
    print("🚀 Access your beautiful dashboard at: http://localhost:8000")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
