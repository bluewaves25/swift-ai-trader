#!/usr/bin/env python3
"""
Agent Monitor
Monitor the status of all trading agents in real-time.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
import redis

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from engine_agents.parallel_agent_runner import ParallelAgentRunner

class AgentMonitor:
    """Monitor all trading agents"""
    
    def __init__(self, config=None):
        self.config = config or {
            "redis_host": "localhost",
            "redis_port": 6379,
            "redis_db": 0
        }
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=self.config['redis_host'],
                port=self.config['redis_port'],
                db=self.config['redis_db'],
                decode_responses=True
            )
            self.redis_client.ping()
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            self.redis_client = None
    
    def get_agent_status(self):
        """Get agent status from Redis"""
        try:
            if not self.redis_client:
                return None
            
            status_data = self.redis_client.get('agent_runner:latest_status')
            if status_data:
                return eval(status_data)
            return None
            
        except Exception as e:
            print(f"❌ Error getting agent status: {e}")
            return None
    
    def display_status(self, status):
        """Display agent status in a nice format"""
        if not status:
            print("❌ No status data available")
            return
        
        print("\n" + "="*60)
        print("🤖 TRADING AGENT STATUS")
        print("="*60)
        
        # Display metrics
        metrics = status.get('metrics', {})
        print(f"📊 Metrics:")
        print(f"   Total Agents: {metrics.get('total_agents', 0)}")
        print(f"   Running: {metrics.get('running_agents', 0)}")
        print(f"   Errors: {metrics.get('error_agents', 0)}")
        print(f"   Total Restarts: {metrics.get('total_restarts', 0)}")
        print(f"   Uptime: {metrics.get('uptime_seconds', 0)}s")
        
        # Display individual agent status
        agents = status.get('agents', {})
        print(f"\n🔍 Agent Details:")
        
        for agent_name, agent_data in agents.items():
            status_emoji = {
                'running': '🟢',
                'stopped': '🔴',
                'starting': '🟡',
                'stopping': '🟡',
                'error': '🔴'
            }
            
            status = agent_data.get('status', 'unknown')
            emoji = status_emoji.get(status, '⚪')
            
            print(f"   {emoji} {agent_name.upper()}: {status}")
            
            if agent_data.get('error_message'):
                print(f"      Error: {agent_data['error_message']}")
            
            if agent_data.get('start_time'):
                uptime = time.time() - agent_data['start_time']
                print(f"      Uptime: {uptime:.1f}s")
            
            if agent_data.get('restart_count', 0) > 0:
                print(f"      Restarts: {agent_data['restart_count']}")
    
    def display_redis_channels(self):
        """Display active Redis channels"""
        try:
            if not self.redis_client:
                return
            
            print(f"\n📡 Redis Channels:")
            
            # Check for active channels
            channels = [
                'core_agent:signal_processing',
                'data_feeds_agent:price_updates',
                'market_conditions_agent:analysis',
                'intelligence_agent:patterns',
                'strategy_engine_agent:compositions',
                'risk_management_agent:assessments',
                'execution_agent:orders',
                'validation_agent:results',
                'fees_monitor_agent:optimizations',
                'adapters_agent:connections',
                'failure_prevention_agent:alerts'
            ]
            
            for channel in channels:
                try:
                    # Try to get subscriber count (this might not work in all Redis setups)
                    # For now, just show the channel names
                    print(f"   📺 {channel}")
                except:
                    print(f"   📺 {channel}")
                    
        except Exception as e:
            print(f"❌ Error checking Redis channels: {e}")
    
    def display_system_health(self):
        """Display overall system health"""
        try:
            if not self.redis_client:
                return
            
            print(f"\n🏥 System Health:")
            
            # Check Redis connection
            try:
                self.redis_client.ping()
                print("   🔗 Redis: Connected")
            except:
                print("   🔗 Redis: Disconnected")
            
            # Check for recent activity
            recent_keys = self.redis_client.keys('*agent*')
            print(f"   📊 Active Keys: {len(recent_keys)}")
            
            # Check for errors
            error_keys = self.redis_client.keys('*error*')
            if error_keys:
                print(f"   ⚠️  Error Keys: {len(error_keys)}")
            else:
                print("   ✅ No Recent Errors")
                
        except Exception as e:
            print(f"❌ Error checking system health: {e}")
    
    def run_monitor(self, interval=5):
        """Run continuous monitoring"""
        print("🔍 Starting Agent Monitor...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Clear screen (works on Unix-like systems)
                print("\033[2J\033[H", end="")
                
                # Get and display status
                status = self.get_agent_status()
                self.display_status(status)
                
                # Display Redis channels
                self.display_redis_channels()
                
                # Display system health
                self.display_system_health()
                
                # Display timestamp
                print(f"\n⏰ Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"🔄 Refreshing every {interval} seconds...")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏹️  Monitor stopped by user")
        except Exception as e:
            print(f"❌ Monitor error: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor trading agents')
    parser.add_argument('--redis-host', default='localhost', help='Redis host')
    parser.add_argument('--redis-port', type=int, default=6379, help='Redis port')
    parser.add_argument('--redis-db', type=int, default=0, help='Redis database')
    parser.add_argument('--interval', type=int, default=5, help='Update interval in seconds')
    parser.add_argument('--once', action='store_true', help='Display status once and exit')
    
    args = parser.parse_args()
    
    # Create configuration
    config = {
        'redis_host': args.redis_host,
        'redis_port': args.redis_port,
        'redis_db': args.redis_db
    }
    
    # Create monitor
    monitor = AgentMonitor(config)
    
    if args.once:
        # Display status once
        status = monitor.get_agent_status()
        monitor.display_status(status)
        monitor.display_redis_channels()
        monitor.display_system_health()
    else:
        # Run continuous monitoring
        monitor.run_monitor(args.interval)

if __name__ == "__main__":
    main()
