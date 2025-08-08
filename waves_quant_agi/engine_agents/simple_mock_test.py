#!/usr/bin/env python3
"""
Simple Mock Data Test
Runs mock data generator and trading engine for testing.
"""

import asyncio
import time
import json
import signal
import sys
from mock_market_data_generator import MockMarketDataGenerator

async def test_mock_data():
    """Test the mock data generator."""
    print("🧪 Testing Mock Market Data Generator")
    print("=" * 50)
    
    config = {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0,
        'symbols': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'],
        'update_interval': 1.0,
        'volatility': 0.02
    }
    
    generator = MockMarketDataGenerator(config)
    
    try:
        print("🚀 Starting mock data generator...")
        await generator.start()
    except KeyboardInterrupt:
        print("\n🛑 Stopping mock data generator...")
        await generator.stop()
    except Exception as e:
        print(f"❌ Error: {e}")
        await generator.stop()

async def test_engine_with_data():
    """Test the trading engine with mock data."""
    print("🧪 Testing Trading Engine with Mock Data")
    print("=" * 50)
    
    # Start mock data generator
    config = {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0,
        'symbols': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'],
        'update_interval': 1.0,
        'volatility': 0.02
    }
    
    generator = MockMarketDataGenerator(config)
    
    try:
        # Start data generator in background
        print("📊 Starting mock data generator...")
        data_task = asyncio.create_task(generator.start())
        
        # Wait for data to start flowing
        await asyncio.sleep(3)
        
        # Start trading engine
        print("🚀 Starting trading engine...")
        from start_trading_engine import main as start_engine
        engine_task = asyncio.create_task(start_engine())
        
        # Run for 30 seconds
        print("⏱️  Running test for 30 seconds...")
        await asyncio.sleep(30)
        
        # Stop both
        print("🛑 Stopping test...")
        generator.is_running = False
        await asyncio.sleep(2)
        
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal")
        generator.is_running = False
    except Exception as e:
        print(f"❌ Error: {e}")
        generator.is_running = False

async def main():
    """Main function."""
    print("Choose test mode:")
    print("1. Test mock data generator only")
    print("2. Test trading engine with mock data")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        await test_mock_data()
    elif choice == "2":
        await test_engine_with_data()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())
