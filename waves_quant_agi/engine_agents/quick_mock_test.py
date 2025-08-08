#!/usr/bin/env python3
"""
Quick Mock Data Test
Simple test of mock data generator.
"""

import asyncio
import time
from mock_market_data_generator import MockMarketDataGenerator

async def quick_test():
    """Quick test of mock data generator."""
    print("🧪 Quick Mock Data Test")
    print("=" * 30)
    
    config = {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0,
        'symbols': ['BTC/USDT', 'ETH/USDT'],
        'update_interval': 1.0,
        'volatility': 0.02
    }
    
    generator = MockMarketDataGenerator(config)
    
    try:
        print("🚀 Starting mock data generator...")
        print("⏱️  Running for 10 seconds...")
        
        # Start generator
        generator.is_running = True
        
        # Create tasks
        tasks = [
            asyncio.create_task(generator._generate_price_data()),
            asyncio.create_task(generator._generate_order_book_data()),
            asyncio.create_task(generator._generate_trade_data()),
            asyncio.create_task(generator._generate_sentiment_data()),
            asyncio.create_task(generator._generate_market_signals()),
            asyncio.create_task(generator._stats_reporting_loop())
        ]
        
        # Run for 10 seconds
        await asyncio.sleep(10)
        
        # Stop
        generator.is_running = False
        print("🛑 Stopping generator...")
        
        # Wait for tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        print("✅ Test completed!")
        print(f"📊 Final stats: {generator.stats}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        generator.is_running = False

if __name__ == "__main__":
    asyncio.run(quick_test())

