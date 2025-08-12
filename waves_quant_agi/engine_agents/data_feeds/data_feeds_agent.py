#!/usr/bin/env python3
"""
Data Feeds Agent - Enhanced with BaseAgent System
Collects and processes market data from multiple sources.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from engine_agents.shared_utils import BaseAgent, register_agent

class DataFeedsAgent(BaseAgent):
    """Data feeds agent using base class with MT5 data fetching."""
    
    def _initialize_agent_components(self):
        """Initialize data feeds specific components."""
        # Initialize data feeds components
        self.price_feeds = {}
        self.sentiment_feeds = {}
        self.order_book_feeds = {}
        self.derived_data_processors = {}
        
        # MT5 data fetching with organized categories
        self.mt5_adapter = None
        self.price_update_interval = 1.0  # seconds
        
        # MT5 symbol categories - will be populated dynamically
        self.mt5_symbols = {
            "forex": [],
            "indices": [],
            "stocks": [],
            "energy": [],
            "crypto": [],
            "crypto_cross": []
        }
        
        # Initialize stats
        self.stats = {
            "price_updates": 0,
            "sentiment_updates": 0,
            "order_book_updates": 0,
            "derived_data_updates": 0,
            "anomalies_detected": 0,
            "mt5_connection_status": "disconnected",
            "last_price_update": 0,
            "forex_updates": 0,
            "indices_updates": 0,
            "stocks_updates": 0,
            "energy_updates": 0,
            "crypto_updates": 0,
            "crypto_cross_updates": 0
        }
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Data feeds specific startup logic."""
        try:
            # Initialize MT5 connection
            await self._init_mt5_connection()
            
            # Initialize price feeds
            self._init_core_price_feeds()
            self._init_streamlined_sentiment_feeds()
            self._init_strategy_order_book_feeds()
            self._init_strategy_derived_data()
            
            self.logger.info("Data feeds agent startup completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in data feeds startup: {e}")
            raise
    
    async def _agent_specific_shutdown(self):
        """Data feeds specific shutdown logic."""
        try:
            if self.mt5_adapter:
                self.mt5_adapter.disconnect()
            self.logger.info("Data feeds agent shutdown completed")
        except Exception as e:
            self.logger.error(f"Error in data feeds shutdown: {e}")
    
    def _get_background_tasks(self) -> List[tuple]:
        """Get background tasks for this agent."""
        return [
            (self._mt5_price_stream(), "MT5 Price Stream", "fast"),
            (self._market_data_processor(), "Market Data Processor", "fast"),
            (self._data_quality_monitor(), "Data Quality Monitor", "tactical"),
            (self._refresh_symbols_periodically(), "Symbol Refresh", "strategic")
        ]
    
    # ============= MT5 DATA FETCHING =============
    
    async def _init_mt5_connection(self):
        """Initialize MT5 connection for data fetching."""
        try:
            # Import MT5 broker
            from engine_agents.adapters.brokers.mt5_plugin import MT5Broker
            
            # Get MT5 credentials from config file
            mt5_config = self.config.get("brokers", {}).get("exness", {})
            login = mt5_config.get("mt5_login")
            password = mt5_config.get("mt5_password")
            server = mt5_config.get("mt5_server")
            
            # Ensure login is an integer
            if login is not None:
                try:
                    login = int(login)
                except (ValueError, TypeError):
                    self.logger.error(f"Invalid MT5_LOGIN value: {login}")
                    raise ValueError("MT5_LOGIN must be a valid integer")
            
            if not all([login, password, server]):
                # Fallback to environment variables
                import os
                login = int(os.getenv('MT5_LOGIN', 0))
                password = os.getenv('MT5_PASSWORD', '')
                server = os.getenv('MT5_SERVER', '')
                
                if not all([login, password, server]):
                    raise ValueError("MT5 credentials not found in config or environment")
            
            # Create MT5 broker instance
            self.mt5_adapter = MT5Broker(login, password, server)
            
            # Connect to MT5
            if self.mt5_adapter.connect():
                self.logger.info("✅ Connected to MT5 successfully")
                self.stats["mt5_connection_status"] = "connected"
                
                # Fetch and categorize all available symbols from MT5
                await self._fetch_mt5_symbols()
                
            else:
                raise ConnectionError("Failed to connect to MT5")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize MT5 connection: {e}")
            self.stats["mt5_connection_status"] = "failed"
            raise
    
    async def _fetch_mt5_symbols(self):
        """Dynamically fetch and categorize all available symbols from MT5."""
        try:
            self.logger.info("🔍 Fetching available symbols from MT5...")
            
            # Get all available symbols from MT5
            all_symbols = self.mt5_adapter.get_all_symbols()
            
            if not all_symbols:
                self.logger.warning("⚠️ No symbols found from MT5, using fallback symbols")
                # Fallback to some common symbols if MT5 doesn't return any
                all_symbols = ["BTCUSD", "ETHUSD", "EURUSD", "GBPUSD", "XAUUSD"]
            
            self.logger.info(f"📊 Found {len(all_symbols)} total symbols from MT5")
            
            # Categorize symbols based on their names
            for symbol in all_symbols:
                symbol_upper = symbol.upper()
                
                # Forex pairs (major and minor)
                if any(pair in symbol_upper for pair in ["EUR", "GBP", "USD", "JPY", "CHF", "AUD", "NZD", "CAD"]) and len(symbol_upper) == 6:
                    self.mt5_symbols["forex"].append(symbol)
                
                # Indices
                elif any(index in symbol_upper for index in ["US30", "SPX", "NAS", "GER", "UK", "FRA", "JPN", "AUS", "SWI", "ITA", "ESP", "NLD"]):
                    self.mt5_symbols["indices"].append(symbol)
                
                # Stocks (common stock symbols)
                elif any(stock in symbol_upper for stock in ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "ADBE", "CRM", "ORCL", "INTC", "AMD", "QCOM"]):
                    self.mt5_symbols["stocks"].append(symbol)
                
                # Energy and commodities
                elif any(energy in symbol_upper for energy in ["XAU", "XAG", "WTI", "BRENT", "NATGAS", "HEATOIL", "GASOLINE", "COPPER", "ALUMINUM", "NICKEL", "ZINC", "LEAD"]):
                    self.mt5_symbols["energy"].append(symbol)
                
                # Crypto (USD pairs)
                elif any(crypto in symbol_upper for crypto in ["BTC", "ETH", "XRP", "LTC", "BCH", "ADA", "DOT", "LINK", "UNI", "SOL", "MATIC", "AVAX"]) and "USD" in symbol_upper:
                    self.mt5_symbols["crypto"].append(symbol)
                
                # Crypto cross pairs (non-USD)
                elif any(crypto in symbol_upper for crypto in ["BTC", "ETH", "XRP", "LTC", "BCH", "ADA", "DOT", "LINK", "UNI", "SOL", "MATIC", "AVAX"]) and "USD" not in symbol_upper:
                    self.mt5_symbols["crypto_cross"].append(symbol)
                
                # If symbol doesn't fit any category, add to forex as default
                else:
                    self.mt5_symbols["forex"].append(symbol)
            
            # Log the categorization results
            for category, symbols in self.mt5_symbols.items():
                if symbols:
                    self.logger.info(f"📈 {category.upper()}: {len(symbols)} symbols - {symbols[:5]}{'...' if len(symbols) > 5 else ''}")
                else:
                    self.logger.warning(f"⚠️ No symbols found for category: {category}")
            
            # Store symbol info in Redis for other agents to use
            symbol_info = {
                'total_symbols': len(all_symbols),
                'categories': {cat: len(syms) for cat, syms in self.mt5_symbols.items()},
                'last_updated': time.time(),
                'source': 'MT5'
            }
            self.redis_conn.hset("mt5_symbols_info", mapping=symbol_info)
            
            self.logger.info("✅ Symbol categorization completed successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error fetching MT5 symbols: {e}")
            # Use minimal fallback symbols to prevent complete failure
            self.mt5_symbols["crypto"] = ["BTCUSD", "ETHUSD"]
            self.mt5_symbols["forex"] = ["EURUSD", "GBPUSD"]
            self.logger.info("🔄 Using fallback symbols due to error")
    
    async def _refresh_symbols_periodically(self):
        """Periodically refresh symbols from MT5 to catch new additions."""
        while self.is_running:
            try:
                # Refresh symbols every hour (3600 seconds)
                await asyncio.sleep(3600)
                
                if self.stats["mt5_connection_status"] == "connected":
                    self.logger.info("🔄 Refreshing symbols from MT5...")
                    await self._fetch_mt5_symbols()
                    
            except Exception as e:
                self.logger.error(f"Error refreshing symbols: {e}")
                await asyncio.sleep(3600)  # Continue trying
    
    async def _mt5_price_stream(self):
        """Stream real-time prices from MT5 with organized categories."""
        while self.is_running:
            try:
                if not self.mt5_adapter or self.stats["mt5_connection_status"] != "connected":
                    await asyncio.sleep(5)
                    continue
                
                # Fetch prices for all symbol categories
                for category, symbols in self.mt5_symbols.items():
                    if not symbols:  # Skip empty categories
                        continue
                    
                    # Limit to first 8 symbols per category to prevent overwhelming
                    symbols_to_fetch = symbols[:8]
                    for symbol in symbols_to_fetch:
                        try:
                            # Get current tick data
                            tick_data = self.mt5_adapter.get_symbol_tick(symbol)
                            
                            if tick_data and tick_data.get('bid') and tick_data.get('ask'):
                                # Store real market data in Redis with category
                                market_data = {
                                    'symbol': symbol,
                                    'category': category,
                                    'bid': float(tick_data['bid']),
                                    'ask': float(tick_data['ask']),
                                    'timestamp': time.time(),
                                    'source': 'MT5',
                                    'volume': tick_data.get('volume', 0),
                                    'spread': float(tick_data['ask']) - float(tick_data['bid'])
                                }
                                
                                # Store in Redis with symbol-specific key
                                redis_key = f"market_data:{symbol}"
                                self.redis_conn.hset(redis_key, mapping=market_data)
                                
                                # Store in category-specific lists
                                category_key = f"market_data:{category}"
                                self.redis_conn.lpush(category_key, json.dumps(market_data))
                                self.redis_conn.ltrim(category_key, 0, 49)  # Keep last 50 per category
                                
                                # Also store in general market data list
                                self.redis_conn.lpush("market_data:latest", json.dumps(market_data))
                                self.redis_conn.ltrim("market_data:latest", 0, 199)  # Keep last 200 total
                                
                                # Update category-specific stats
                                self.stats[f"{category}_updates"] += 1
                                self.stats["price_updates"] += 1
                                self.stats["last_price_update"] = time.time()
                                
                                self.logger.debug(f"📈 Updated {category.upper()} {symbol}: Bid {market_data['bid']:.5f}, Ask {market_data['ask']:.5f}")
                        
                        except Exception as e:
                            self.logger.error(f"Error fetching {category} {symbol}: {e}")
                            continue
                
                # Wait before next update
                await asyncio.sleep(self.price_update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in MT5 price stream: {e}")
                await asyncio.sleep(5)
    
    async def _market_data_processor(self):
        """Process and validate market data."""
        while self.is_running:
            try:
                # Get latest market data
                latest_data = self.redis_conn.lrange("market_data:latest", 0, 0)
                
                if latest_data:
                    data = json.loads(latest_data[0])
                    
                    # Validate data quality
                    if self._validate_market_data(data):
                        # Send to strategy engine
                        await self._send_to_strategy_engine(data)
                        
                        # Update performance metrics
                        self._update_performance_metrics(data)
                
                await asyncio.sleep(0.1)  # 100ms
                
            except Exception as e:
                self.logger.error(f"Error in market data processor: {e}")
                await asyncio.sleep(1)
    
    async def _data_quality_monitor(self):
        """Monitor data quality and detect anomalies."""
        while self.is_running:
            try:
                # Check data freshness
                if self.stats["last_price_update"] > 0:
                    time_since_update = time.time() - self.stats["last_price_update"]
                    
                    if time_since_update > 30:  # 30 seconds
                        self.logger.warning(f"⚠️ Data feed stale: {time_since_update:.1f}s since last update")
                        
                        # Try to reconnect to MT5
                        if self.stats["mt5_connection_status"] == "connected":
                            await self._reconnect_mt5()
                
                # Check for price anomalies
                # await self._detect_price_anomalies()  # TODO: Implement price anomaly detection
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in data quality monitor: {e}")
                await asyncio.sleep(30)
    
    # ============= HELPER METHODS =============
    
    def _validate_market_data(self, data: Dict[str, Any]) -> bool:
        """Validate market data quality."""
        try:
            required_fields = ['symbol', 'bid', 'ask', 'timestamp']
            if not all(field in data for field in required_fields):
                return False
            
            # Check for reasonable price values
            if data['bid'] <= 0 or data['ask'] <= 0:
                return False
            
            # Check for reasonable spread
            spread = data['ask'] - data['bid']
            if spread < 0 or spread > data['bid'] * 0.1:  # Max 10% spread
                return False
            
            return True
            
        except Exception:
            return False
    
    async def _send_to_strategy_engine(self, data: Dict[str, Any]):
        """Send market data to strategy engine."""
        try:
            # Publish to strategy engine channel
            message = {
                'type': 'market_data_update',
                'data': data,
                'timestamp': time.time(),
                'source': 'data_feeds'
            }
            
            self.redis_conn.publish('strategy_engine:market_data', json.dumps(message))
            
        except Exception as e:
            self.logger.error(f"Error sending to strategy engine: {e}")
    
    def _update_performance_metrics(self, data: Dict[str, Any]):
        """Update performance metrics."""
        try:
            # Update Redis stats with category breakdown
            self.redis_conn.hset(f"agent_stats:{self.agent_name}", mapping={
                'price_updates': self.stats["price_updates"],
                'last_price_update': self.stats["last_price_update"],
                'mt5_connection_status': self.stats["mt5_connection_status"],
                'forex_updates': self.stats["forex_updates"],
                'indices_updates': self.stats["indices_updates"],
                'stocks_updates': self.stats["stocks_updates"],
                'energy_updates': self.stats["energy_updates"],
                'crypto_updates': self.stats["crypto_updates"],
                'crypto_cross_updates': self.stats["crypto_cross_updates"],
                'total_symbols': sum(len(symbols) for symbols in self.mt5_symbols.values()),
                'timestamp': time.time()
            })
            
        except Exception as e:
            self.logger.error(f"Error updating performance metrics: {e}")
    
    async def _reconnect_mt5(self):
        """Reconnect to MT5 if connection is lost."""
        try:
            self.logger.info("🔄 Attempting to reconnect to MT5...")
            
            if self.mt5_adapter:
                self.mt5_adapter.disconnect()
            
            await self._init_mt5_connection()
            
        except Exception as e:
            self.logger.error(f"Failed to reconnect to MT5: {e}")
    
    # ============= LEGACY INIT METHODS (simplified) =============
    
    def _init_core_price_feeds(self):
        """Initialize core price feeds."""
        self.logger.info("Initializing core price feeds")
    
    def _init_streamlined_sentiment_feeds(self):
        """Initialize streamlined sentiment feeds."""
        self.logger.info("Initializing sentiment feeds")
    
    def _init_strategy_order_book_feeds(self):
        """Initialize strategy-specific order book feeds."""
        self.logger.info("Initializing order book feeds")
    
    def _init_strategy_derived_data(self):
        """Initialize strategy-specific derived data."""
        self.logger.info("Initializing derived data processors") 