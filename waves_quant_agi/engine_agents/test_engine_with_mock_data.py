#!/usr/bin/env python3
"""
Test Trading Engine with Mock Market Data
Runs the trading engine alongside mock market data to test system performance.
"""

import asyncio
import time
import json
import signal
import sys
from typing import Dict, Any
from parallel_agent_runner import ParallelAgentRunner
from mock_market_data_generator import MockMarketDataGenerator

class EngineTester:
    """Test runner for trading engine with mock data."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.is_running = False
        
        # Initialize components
        self.engine = None
        self.data_generator = None
        
        # Test configuration
        self.test_duration = self.config.get('test_duration', 60)  # seconds
        self.engine_startup_delay = self.config.get('engine_startup_delay', 5)  # seconds
        
        # Statistics
        self.stats = {
            'engine_start_time': None,
            'data_generator_start_time': None,
            'signals_processed': 0,
            'trades_executed': 0,
            'errors_encountered': 0
        }
    
    async def start_test(self):
        """Start the comprehensive engine test."""
        print("🧪 Starting Trading Engine Test with Mock Data")
        print("=" * 60)
        
        self.is_running = True
        
        try:
            # Start mock data generator first
            print("📊 Starting Mock Market Data Generator...")
            self.data_generator = MockMarketDataGenerator(self.config)
            self.stats['data_generator_start_time'] = time.time()
            
            # Start data generator in background
            data_task = asyncio.create_task(self.data_generator.start())
            
            # Wait for data generator to initialize
            await asyncio.sleep(2)
            
            # Start trading engine
            print(f"⏳ Waiting {self.engine_startup_delay}s before starting trading engine...")
            await asyncio.sleep(self.engine_startup_delay)
            
            print("🚀 Starting Trading Engine...")
            self.engine = ParallelAgentRunner(self.config)
            self.stats['engine_start_time'] = time.time()
            
            # Start engine in background
            engine_task = asyncio.create_task(self.engine.start())
            
            # Start monitoring tasks
            monitor_task = asyncio.create_task(self._monitor_test())
            stats_task = asyncio.create_task(self._report_test_stats())
            
            # Run test for specified duration
            print(f"⏱️  Running test for {self.test_duration} seconds...")
            await asyncio.sleep(self.test_duration)
            
            # Stop components
            print("🛑 Stopping test components...")
            await self._stop_test()
            
            # Wait for tasks to complete
            await asyncio.gather(data_task, engine_task, monitor_task, stats_task, return_exceptions=True)
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            await self._stop_test()
        finally:
            self.is_running = False
    
    async def _stop_test(self):
        """Stop all test components."""
        try:
            if self.data_generator:
                await self.data_generator.stop()
            
            if self.engine:
                await self.engine.stop()
                
        except Exception as e:
            print(f"❌ Error stopping test components: {e}")
    
    async def _monitor_test(self):
        """Monitor test progress and system health."""
        while self.is_running:
            try:
                # Check Redis for data flow
                if hasattr(self.data_generator, 'redis_client') and self.data_generator.redis_client:
                    # Check if data is being published
                    price_keys = self.data_generator.redis_client.keys('latest_price:*')
                    signal_keys = self.data_generator.redis_client.keys('signal_history')
                    
                    if price_keys and signal_keys:
                        print("✅ Data flow: Market data and signals are being generated")
                    else:
                        print("⚠️  Data flow: Some data streams may not be active")
                
                # Check engine status
                if self.engine:
                    engine_status = self.engine.get_agent_status()
                    if engine_status.get('is_running'):
                        print("✅ Engine: Trading engine is running")
                    else:
                        print("⚠️  Engine: Trading engine may have issues")
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _report_test_stats(self):
        """Report comprehensive test statistics."""
        while self.is_running:
            try:
                uptime = time.time() - (self.stats['engine_start_time'] or time.time())
                
                print(f"\n📈 Test Statistics (Uptime: {uptime:.1f}s):")
                print("-" * 40)
                
                # Data generator stats
                if self.data_generator and hasattr(self.data_generator, 'stats'):
                    dg_stats = self.data_generator.stats
                    print(f"📊 Mock Data Generator:")
                    print(f"   Price updates: {dg_stats.get('price_updates', 0)}")
                    print(f"   Order book updates: {dg_stats.get('order_book_updates', 0)}")
                    print(f"   Trade updates: {dg_stats.get('trade_updates', 0)}")
                    print(f"   Sentiment updates: {dg_stats.get('sentiment_updates', 0)}")
                
                # Engine stats
                if self.engine:
                    engine_status = self.engine.get_agent_status()
                    print(f"🚀 Trading Engine:")
                    print(f"   Status: {'Running' if engine_status.get('is_running') else 'Stopped'}")
                    print(f"   Agents: {len(engine_status.get('agents', {}))}")
                
                # Redis data check
                if hasattr(self.data_generator, 'redis_client') and self.data_generator.redis_client:
                    try:
                        # Count various data types in Redis
                        price_count = len(self.data_generator.redis_client.keys('latest_price:*'))
                        signal_count = len(self.data_generator.redis_client.lrange('signal_history', 0, -1))
                        trade_count = sum([
                            len(self.data_generator.redis_client.lrange(f'trade_history:{symbol}', 0, -1))
                            for symbol in self.data_generator.symbols
                        ])
                        
                        print(f"💾 Redis Data:")
                        print(f"   Active symbols: {price_count}")
                        print(f"   Trading signals: {signal_count}")
                        print(f"   Trade records: {trade_count}")
                        
                    except Exception as e:
                        print(f"   Redis check error: {e}")
                
                await asyncio.sleep(15)  # Report every 15 seconds
                
            except Exception as e:
                print(f"❌ Stats reporting error: {e}")
                await asyncio.sleep(5)
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get comprehensive test summary."""
        summary = {
            'test_duration': self.test_duration,
            'engine_runtime': time.time() - (self.stats['engine_start_time'] or time.time()),
            'data_generator_runtime': time.time() - (self.stats['data_generator_start_time'] or time.time()),
            'components': {
                'engine_running': self.engine is not None,
                'data_generator_running': self.data_generator is not None
            }
        }
        
        # Add data generator stats
        if self.data_generator and hasattr(self.data_generator, 'stats'):
            summary['data_generator_stats'] = self.data_generator.stats
        
        # Add engine stats
        if self.engine:
            summary['engine_stats'] = self.engine.get_agent_status()
        
        return summary

async def main():
    """Main test function."""
    config = {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0,
        'test_duration': 120,  # 2 minutes
        'engine_startup_delay': 5,
        'symbols': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT'],
        'update_interval': 1.0,
        'volatility': 0.02
    }
    
    tester = EngineTester(config)
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        print("\n🛑 Received interrupt signal, stopping test...")
        asyncio.create_task(tester._stop_test())
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await tester.start_test()
        
        # Print final summary
        summary = tester.get_test_summary()
        print("\n" + "=" * 60)
        print("🏁 TEST COMPLETED")
        print("=" * 60)
        print(f"Test Duration: {summary['test_duration']} seconds")
        print(f"Engine Runtime: {summary['engine_runtime']:.1f} seconds")
        print(f"Data Generator Runtime: {summary['data_generator_runtime']:.1f} seconds")
        print(f"Engine Running: {summary['components']['engine_running']}")
        print(f"Data Generator Running: {summary['components']['data_generator_running']}")
        
        if 'data_generator_stats' in summary:
            stats = summary['data_generator_stats']
            print(f"\n📊 Data Generated:")
            print(f"   Price updates: {stats.get('price_updates', 0)}")
            print(f"   Order book updates: {stats.get('order_book_updates', 0)}")
            print(f"   Trade updates: {stats.get('trade_updates', 0)}")
            print(f"   Sentiment updates: {stats.get('sentiment_updates', 0)}")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
