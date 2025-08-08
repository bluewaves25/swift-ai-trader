#!/usr/bin/env python3
"""
Mock Market Data Generator
Generates realistic mock market data for testing the trading engine.
"""

import asyncio
import time
import json
import random
import redis
from typing import Dict, Any, List
from datetime import datetime, timedelta
import math

class MockMarketDataGenerator:
    """Generates realistic mock market data for engine testing."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.is_running = False
        
        # Initialize Redis connection
        self.redis_client = self._init_redis()
        
        # Market data configuration
        self.symbols = self.config.get('symbols', ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT'])
        self.update_interval = self.config.get('update_interval', 1.0)  # seconds
        self.volatility = self.config.get('volatility', 0.02)  # 2% volatility
        
        # Base prices for each symbol
        self.base_prices = {
            'BTC/USDT': 45000.0,
            'ETH/USDT': 2800.0,
            'BNB/USDT': 320.0,
            'ADA/USDT': 0.45,
            'SOL/USDT': 95.0
        }
        
        # Current prices (will be updated)
        self.current_prices = self.base_prices.copy()
        
        # Market state
        self.market_trend = 0.0  # -1 to 1 (bearish to bullish)
        self.volume_multiplier = 1.0
        self.volatility_multiplier = 1.0
        
        # Statistics
        self.stats = {
            'price_updates': 0,
            'order_book_updates': 0,
            'trade_updates': 0,
            'sentiment_updates': 0,
            'start_time': time.time()
        }
        
    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            return redis.Redis(
                host=self.config.get("redis_host", "localhost"),
                port=self.config.get("redis_port", 6379),
                db=self.config.get("redis_db", 0),
                decode_responses=True
            )
        except Exception as e:
            print(f"Failed to initialize Redis: {e}")
            return None
    
    async def start(self):
        """Start generating mock market data."""
        if self.is_running:
            return
            
        self.is_running = True
        print("🚀 Starting Mock Market Data Generator...")
        print(f"📊 Symbols: {', '.join(self.symbols)}")
        print(f"⏱️  Update interval: {self.update_interval}s")
        print(f"📈 Volatility: {self.volatility * 100}%")
        
        # Start data generation tasks
        tasks = [
            asyncio.create_task(self._generate_price_data()),
            asyncio.create_task(self._generate_order_book_data()),
            asyncio.create_task(self._generate_trade_data()),
            asyncio.create_task(self._generate_sentiment_data()),
            asyncio.create_task(self._generate_market_signals()),
            asyncio.create_task(self._stats_reporting_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            print("🛑 Mock data generator stopped")
        finally:
            self.is_running = False
    
    async def stop(self):
        """Stop generating mock market data."""
        self.is_running = False
        print("🛑 Stopping Mock Market Data Generator...")
    
    def _generate_price_change(self, symbol: str) -> float:
        """Generate realistic price change for a symbol."""
        base_price = self.current_prices[symbol]
        
        # Random walk with trend influence
        random_change = random.gauss(0, self.volatility * self.volatility_multiplier)
        trend_influence = self.market_trend * 0.001  # Small trend influence
        
        # Add some mean reversion
        price_deviation = (base_price - self.base_prices[symbol]) / self.base_prices[symbol]
        mean_reversion = -price_deviation * 0.01
        
        total_change = random_change + trend_influence + mean_reversion
        
        # Update current price
        new_price = base_price * (1 + total_change)
        self.current_prices[symbol] = max(new_price, 0.01)  # Ensure positive price
        
        return total_change
    
    async def _generate_price_data(self):
        """Generate and publish price data."""
        print("📈 Starting price data generation...")
        
        while self.is_running:
            try:
                timestamp = int(time.time() * 1000)  # milliseconds
                
                for symbol in self.symbols:
                    price_change = self._generate_price_change(symbol)
                    current_price = self.current_prices[symbol]
                    
                    price_data = {
                        'symbol': symbol,
                        'price': current_price,
                        'change': price_change,
                        'change_percent': price_change * 100,
                        'timestamp': timestamp,
                        'source': 'mock_generator',
                        'type': 'price_update'
                    }
                    
                    # Publish to Redis
                    if self.redis_client:
                        # Publish to price feed channel
                        self.redis_client.publish('market_data:price', json.dumps(price_data))
                        
                        # Store in price history
                        self.redis_client.lpush(f'price_history:{symbol}', json.dumps(price_data))
                        self.redis_client.ltrim(f'price_history:{symbol}', 0, 999)  # Keep last 1000
                        
                        # Store latest price
                        self.redis_client.set(f'latest_price:{symbol}', json.dumps(price_data))
                    
                    self.stats['price_updates'] += 1
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                print(f"❌ Error generating price data: {e}")
                await asyncio.sleep(1)
    
    async def _generate_order_book_data(self):
        """Generate and publish order book data."""
        print("📚 Starting order book data generation...")
        
        while self.is_running:
            try:
                timestamp = int(time.time() * 1000)
                
                for symbol in self.symbols:
                    current_price = self.current_prices[symbol]
                    
                    # Generate realistic order book
                    order_book = self._create_order_book(current_price, symbol)
                    
                    order_book_data = {
                        'symbol': symbol,
                        'bids': order_book['bids'],
                        'asks': order_book['asks'],
                        'timestamp': timestamp,
                        'source': 'mock_generator',
                        'type': 'order_book_update'
                    }
                    
                    # Publish to Redis
                    if self.redis_client:
                        self.redis_client.publish('market_data:order_book', json.dumps(order_book_data))
                        self.redis_client.set(f'order_book:{symbol}', json.dumps(order_book_data))
                    
                    self.stats['order_book_updates'] += 1
                
                await asyncio.sleep(self.update_interval * 2)  # Slower updates for order book
                
            except Exception as e:
                print(f"❌ Error generating order book data: {e}")
                await asyncio.sleep(1)
    
    def _create_order_book(self, price: float, symbol: str) -> Dict[str, List]:
        """Create realistic order book data."""
        # Determine price precision based on symbol
        if 'BTC' in symbol or 'ETH' in symbol:
            price_precision = 0.01
        elif 'BNB' in symbol or 'SOL' in symbol:
            price_precision = 0.001
        else:
            price_precision = 0.0001
        
        # Generate bids (buy orders)
        bids = []
        for i in range(10):
            bid_price = price * (1 - (i + 1) * 0.001)  # Slightly below market
            bid_price = round(bid_price / price_precision) * price_precision
            bid_volume = random.uniform(0.1, 2.0) * self.volume_multiplier
            bids.append([bid_price, bid_volume])
        
        # Generate asks (sell orders)
        asks = []
        for i in range(10):
            ask_price = price * (1 + (i + 1) * 0.001)  # Slightly above market
            ask_price = round(ask_price / price_precision) * price_precision
            ask_volume = random.uniform(0.1, 2.0) * self.volume_multiplier
            asks.append([ask_price, ask_volume])
        
        return {'bids': bids, 'asks': asks}
    
    async def _generate_trade_data(self):
        """Generate and publish trade data."""
        print("💱 Starting trade data generation...")
        
        while self.is_running:
            try:
                timestamp = int(time.time() * 1000)
                
                for symbol in self.symbols:
                    current_price = self.current_prices[symbol]
                    
                    # Generate random trade
                    trade_price = current_price * random.uniform(0.999, 1.001)
                    trade_volume = random.uniform(0.01, 1.0) * self.volume_multiplier
                    trade_side = random.choice(['buy', 'sell'])
                    
                    trade_data = {
                        'symbol': symbol,
                        'price': trade_price,
                        'volume': trade_volume,
                        'side': trade_side,
                        'timestamp': timestamp,
                        'trade_id': f"mock_trade_{timestamp}_{random.randint(1000, 9999)}",
                        'source': 'mock_generator',
                        'type': 'trade_update'
                    }
                    
                    # Publish to Redis
                    if self.redis_client:
                        self.redis_client.publish('market_data:trades', json.dumps(trade_data))
                        self.redis_client.lpush(f'trade_history:{symbol}', json.dumps(trade_data))
                        self.redis_client.ltrim(f'trade_history:{symbol}', 0, 999)
                    
                    self.stats['trade_updates'] += 1
                
                await asyncio.sleep(self.update_interval * 0.5)  # Faster updates for trades
                
            except Exception as e:
                print(f"❌ Error generating trade data: {e}")
                await asyncio.sleep(1)
    
    async def _generate_sentiment_data(self):
        """Generate and publish sentiment data."""
        print("😊 Starting sentiment data generation...")
        
        while self.is_running:
            try:
                timestamp = int(time.time() * 1000)
                
                # Generate market sentiment
                sentiment_score = random.uniform(-1, 1)  # -1 to 1
                sentiment_data = {
                    'sentiment_score': sentiment_score,
                    'confidence': random.uniform(0.7, 0.95),
                    'source': 'twitter',
                    'timestamp': timestamp,
                    'type': 'sentiment_update'
                }
                
                # Generate news sentiment
                news_sentiment = {
                    'sentiment_score': random.uniform(-0.8, 0.8),
                    'confidence': random.uniform(0.6, 0.9),
                    'source': 'news',
                    'timestamp': timestamp,
                    'type': 'sentiment_update'
                }
                
                # Publish to Redis
                if self.redis_client:
                    self.redis_client.publish('market_data:sentiment', json.dumps(sentiment_data))
                    self.redis_client.publish('market_data:news_sentiment', json.dumps(news_sentiment))
                    self.redis_client.set('latest_sentiment', json.dumps(sentiment_data))
                
                self.stats['sentiment_updates'] += 1
                
                await asyncio.sleep(self.update_interval * 3)  # Slower updates for sentiment
                
            except Exception as e:
                print(f"❌ Error generating sentiment data: {e}")
                await asyncio.sleep(1)
    
    async def _generate_market_signals(self):
        """Generate trading signals based on market conditions."""
        print("📡 Starting market signal generation...")
        
        while self.is_running:
            try:
                timestamp = int(time.time() * 1000)
                
                # Update market trend based on price movements
                total_change = sum([
                    (self.current_prices[symbol] - self.base_prices[symbol]) / self.base_prices[symbol]
                    for symbol in self.symbols
                ]) / len(self.symbols)
                
                self.market_trend = max(-1, min(1, total_change * 10))  # Normalize to -1 to 1
                
                # Generate trading signals
                for symbol in self.symbols:
                    current_price = self.current_prices[symbol]
                    base_price = self.base_prices[symbol]
                    price_change = (current_price - base_price) / base_price
                    
                    # Simple signal generation logic
                    signal_strength = 0
                    signal_type = 'neutral'
                    
                    if price_change > 0.05:  # 5% increase
                        signal_strength = min(1, price_change * 10)
                        signal_type = 'buy'
                    elif price_change < -0.05:  # 5% decrease
                        signal_strength = min(1, abs(price_change) * 10)
                        signal_type = 'sell'
                    
                    if signal_strength > 0.3:  # Only generate signals above threshold
                        signal_data = {
                            'symbol': symbol,
                            'signal_type': signal_type,
                            'signal_strength': signal_strength,
                            'price': current_price,
                            'price_change': price_change,
                            'timestamp': timestamp,
                            'source': 'mock_signal_generator',
                            'type': 'trading_signal'
                        }
                        
                        # Publish to Redis
                        if self.redis_client:
                            self.redis_client.publish('trading_signals', json.dumps(signal_data))
                            self.redis_client.lpush('signal_history', json.dumps(signal_data))
                            self.redis_client.ltrim('signal_history', 0, 999)
                
                await asyncio.sleep(self.update_interval * 5)  # Slower updates for signals
                
            except Exception as e:
                print(f"❌ Error generating market signals: {e}")
                await asyncio.sleep(1)
    
    async def _stats_reporting_loop(self):
        """Report statistics periodically."""
        while self.is_running:
            try:
                uptime = time.time() - self.stats['start_time']
                print(f"\n📊 Mock Data Generator Stats (Uptime: {uptime:.1f}s):")
                print(f"   Price updates: {self.stats['price_updates']}")
                print(f"   Order book updates: {self.stats['order_book_updates']}")
                print(f"   Trade updates: {self.stats['trade_updates']}")
                print(f"   Sentiment updates: {self.stats['sentiment_updates']}")
                print(f"   Market trend: {self.market_trend:.3f}")
                print(f"   Current prices: {dict([(k, f'{v:.4f}') for k, v in self.current_prices.items()])}")
                
                await asyncio.sleep(10)  # Report every 10 seconds
                
            except Exception as e:
                print(f"❌ Error in stats reporting: {e}")
                await asyncio.sleep(1)

async def main():
    """Main function to run the mock market data generator."""
    config = {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0,
        'symbols': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'SOL/USDT'],
        'update_interval': 1.0,
        'volatility': 0.02
    }
    
    generator = MockMarketDataGenerator(config)
    
    try:
        await generator.start()
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal")
        await generator.stop()

if __name__ == "__main__":
    asyncio.run(main())
