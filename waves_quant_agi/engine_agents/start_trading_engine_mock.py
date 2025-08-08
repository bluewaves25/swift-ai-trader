#!/usr/bin/env python3
"""
Start Trading Engine with Mock Redis
Simple script to start all trading agents in parallel using mock Redis for testing.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

# Import and patch mock Redis before importing the agent runner
from engine_agents.mock_redis import patch_redis
patch_redis()

from engine_agents.parallel_agent_runner import ParallelAgentRunner, run_all_agents

def load_config():
    """Load configuration from file or create default"""
    config_file = Path(__file__).parent / "trading_engine_config.json"
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config file: {e}")
    
    # Default configuration with mock Redis
    return {
        "redis_host": "localhost",
        "redis_port": 6379,
        "redis_db": 0,
        "heartbeat_interval": 30,
        "restart_delay": 5,
        "max_restarts": 3,
        "use_mock_redis": True,  # Flag to indicate mock Redis usage
        
        # Agent-specific configurations
        "core": {
            "cycle_interval": 60,
            "monitoring_interval": 10,
            "reporting_interval": 30
        },
        "data_feeds": {
            "update_interval": 1,
            "max_retries": 3,
            "retry_delay": 1
        },
        "market_conditions": {
            "analysis_interval": 30,
            "anomaly_threshold": 2.0
        },
        "intelligence": {
            "learning_interval": 300,
            "pattern_detection_interval": 60
        },
        "strategy_engine": {
            "composition_interval": 300,
            "performance_check_interval": 60
        },
        "risk_management": {
            "evaluation_interval": 30,
            "risk_threshold": 0.8
        },
        "execution": {
            "latency_threshold": 100,
            "max_slippage": 0.001
        },
        "validation": {
            "validation_interval": 60,
            "strict_mode": True
        },
        "fees_monitor": {
            "optimization_interval": 300,
            "cost_threshold": 0.002
        },
        "adapters": {
            "health_check_interval": 60,
            "connection_timeout": 30
        },
        "failure_prevention": {
            "monitoring_interval": 30,
            "alert_threshold": 3
        }
    }

def save_config(config):
    """Save configuration to file"""
    config_file = Path(__file__).parent / "trading_engine_config.json"
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration saved to {config_file}")
    except Exception as e:
        print(f"Error saving config: {e}")

async def main():
    """Main function to start the trading engine with mock Redis"""
    print("🚀 Starting Trading Engine with Mock Redis...")
    print("=" * 60)
    print("📝 NOTE: This is using Mock Redis for testing")
    print("📝 For production, install Redis and use start_trading_engine.py")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    print(f"📋 Loaded configuration")
    print(f"🔗 Mock Redis: {config['redis_host']}:{config['redis_port']}")
    print(f"⏱️  Heartbeat interval: {config['heartbeat_interval']}s")
    print(f"🔄 Max restarts: {config['max_restarts']}")
    
    # Save config if it doesn't exist
    config_file = Path(__file__).parent / "trading_engine_config.json"
    if not config_file.exists():
        save_config(config)
    
    print("\n📊 Agent Status:")
    print("- Core Agent: Orchestrator")
    print("- Data Feeds Agent: Market data collection")
    print("- Market Conditions Agent: Supply/demand analysis")
    print("- Intelligence Agent: Pattern recognition")
    print("- Strategy Engine Agent: Strategy composition")
    print("- Risk Management Agent: Risk assessment")
    print("- Execution Bridge: Order execution")
    print("- Validation Bridge: Strategy validation")
    print("- Fees Monitor Agent: Cost optimization")
    print("- Adapters Agent: Broker management")
    print("- Failure Prevention Agent: System health")
    
    print("\n🔄 Starting all agents in parallel with Mock Redis...")
    print("Press Ctrl+C to stop gracefully")
    print("=" * 60)
    
    try:
        # Run all agents
        await run_all_agents(config)
        
    except KeyboardInterrupt:
        print("\n⏹️  Received interrupt signal")
        print("🛑 Stopping all agents gracefully...")
    except Exception as e:
        print(f"❌ Error running trading engine: {e}")
        return 1
    
    print("✅ Trading engine stopped successfully")
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
