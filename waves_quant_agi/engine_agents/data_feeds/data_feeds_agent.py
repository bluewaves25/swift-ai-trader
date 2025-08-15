#!/usr/bin/env python3
"""
Data Feeds Agent - ROLE CONSOLIDATED: DATA FEEDS ONLY
Removed data validation functionality - now handled by Validation Agent.
Focuses exclusively on collecting, processing, and distributing market data from multiple sources.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from engine_agents.shared_utils import BaseAgent, register_agent

class DataFeedsAgent(BaseAgent):
    """Data feeds agent - focused solely on data collection and distribution."""
    
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
        
        # Data feeds state
        self.data_feeds_state = {
            "active_feeds": {},
            "feed_status": {},
            "last_data_update": time.time(),
            "data_distribution_status": "initializing"
        }
        
        # Data feeds statistics
        self.stats = {
            "price_updates": 0,
            "sentiment_updates": 0,
            "order_book_updates": 0,
            "derived_data_updates": 0,
            "mt5_connection_status": "disconnected",
            "last_price_update": 0,
            "forex_updates": 0,
            "indices_updates": 0,
            "stocks_updates": 0,
            "energy_updates": 0,
            "crypto_updates": 0,
            "crypto_cross_updates": 0,
            "start_time": time.time()
        }
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Data feeds specific startup logic."""
        try:
            # Initialize MT5 connection
            await self._init_mt5_connection()
            
            # Initialize data feed components
            await self._initialize_data_feed_components()
            
            # Initialize data distribution systems
            await self._initialize_data_distribution()
            
            self.logger.info("✅ Data Feeds Agent: Data collection systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error in data feeds startup: {e}")
            raise
    
    async def _agent_specific_shutdown(self):
        """Data feeds specific shutdown logic."""
        try:
            # Cleanup data feed resources
            await self._cleanup_data_feed_components()
            
            if self.mt5_adapter:
                self.mt5_adapter.disconnect()
                
            self.logger.info("✅ Data Feeds Agent: Data collection systems shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in data feeds shutdown: {e}")
    
    # ============= BACKGROUND TASKS =============
    
    async def _data_collection_loop(self):
        """Data collection loop."""
        while self.is_running:
            try:
                # Collect data from various sources
                await self._collect_mt5_data()
                await self._collect_market_data()
                
                await asyncio.sleep(1.0)  # 1 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in data collection loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _data_quality_monitoring_loop(self):
        """Data quality monitoring loop."""
        while self.is_running:
            try:
                # Monitor data quality
                await self._check_data_quality()
                
                await asyncio.sleep(5.0)  # 5 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in data quality monitoring loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _market_data_processing_loop(self):
        """Market data processing loop."""
        while self.is_running:
            try:
                # Process market data
                await self._process_market_data()
                
                await asyncio.sleep(0.5)  # 500ms cycle
                
            except Exception as e:
                self.logger.error(f"Error in market data processing loop: {e}")
                await asyncio.sleep(0.5)
    
    async def _data_feeds_health_monitoring_loop(self):
        """Data feeds health monitoring loop."""
        while self.is_running:
            try:
                # Monitor data feeds health
                await self._check_data_feeds_health()
                
                await asyncio.sleep(10.0)  # 10 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in data feeds health monitoring loop: {e}")
                await asyncio.sleep(10.0)
    
    async def _collect_mt5_data(self):
        """Collect data from MT5."""
        try:
            # Placeholder for MT5 data collection
            pass
        except Exception as e:
            self.logger.error(f"Error collecting MT5 data: {e}")
    
    async def _collect_market_data(self):
        """Collect market data."""
        try:
            # Placeholder for market data collection
            pass
        except Exception as e:
            self.logger.error(f"Error collecting market data: {e}")
    
    async def _check_data_quality(self):
        """Check data quality."""
        try:
            # Placeholder for data quality check
            pass
        except Exception as e:
            self.logger.error(f"Error checking data quality: {e}")
    
    async def _process_market_data(self):
        """Process market data."""
        try:
            # Placeholder for market data processing
            pass
        except Exception as e:
            self.logger.error(f"Error processing market data: {e}")
    
    async def _check_data_feeds_health(self):
        """Check data feeds health."""
        try:
            # Placeholder for data feeds health check
            pass
        except Exception as e:
            self.logger.error(f"Error checking data feeds health: {e}")

    def _get_background_tasks(self) -> List[tuple]:
        """Get background tasks for this agent."""
        return [
            (self._data_collection_loop, "Data Collection", "fast"),
            (self._data_distribution_loop, "Data Distribution", "fast"),
            (self._data_quality_monitoring_loop, "Data Quality Monitoring", "tactical"),
            (self._market_data_processing_loop, "Market Data Processing", "fast"),
            (self._data_feeds_health_monitoring_loop, "Data Feeds Health Monitoring", "tactical")
        ]
    
    # ============= DATA FEED COMPONENT INITIALIZATION =============
    
    async def _initialize_data_feed_components(self):
        """Initialize data feed components."""
        try:
            # Initialize price feeds
            self._init_core_price_feeds()
            
            # Initialize sentiment feeds
            self._init_streamlined_sentiment_feeds()
            
            # Initialize order book feeds
            self._init_strategy_order_book_feeds()
            
            # Initialize derived data processors
            self._init_strategy_derived_data()
            
            self.logger.info("✅ Data feed components initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing data feed components: {e}")
            raise
    
    async def _initialize_data_distribution(self):
        """Initialize data distribution systems."""
        try:
            # Initialize data distribution channels
            await self._setup_data_distribution_channels()
            
            # Initialize feed monitoring
            await self._setup_feed_monitoring()
            
            self.logger.info("✅ Data distribution systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing data distribution: {e}")
            raise
    
    async def _cleanup_data_feed_components(self):
        """Cleanup data feed components."""
        try:
            # Cleanup price feeds
            self.price_feeds.clear()
            
            # Cleanup sentiment feeds
            self.sentiment_feeds.clear()
            
            # Cleanup order book feeds
            self.order_book_feeds.clear()
            
            # Cleanup derived data processors
            self.derived_data_processors.clear()
            
            self.logger.info("✅ Data feed components cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up data feed components: {e}")
    
    # ============= DATA DISTRIBUTION SETUP =============
    
    async def _setup_data_distribution_channels(self):
        """Setup data distribution channels."""
        try:
            # Setup Redis channels for data distribution
            self.data_channels = {
                "price_updates": "market_data:price",
                "sentiment_updates": "market_data:sentiment",
                "order_book_updates": "market_data:orderbook",
                "derived_data": "market_data:derived"
            }
            
            self.logger.info("✅ Data distribution channels setup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up data distribution channels: {e}")
            raise
    
    async def _setup_feed_monitoring(self):
        """Setup feed monitoring."""
        try:
            # Initialize feed status monitoring
            self.feed_monitors = {}
            
            for feed_type in ["price", "sentiment", "orderbook", "derived"]:
                self.feed_monitors[feed_type] = {
                    "status": "active",
                    "last_update": time.time(),
                    "update_count": 0
                }
            
            self.logger.info("✅ Feed monitoring setup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up feed monitoring: {e}")
            raise
    
    # ============= BACKGROUND TASK LOOPS =============
    
    async def _data_distribution_loop(self):
        """Data distribution loop."""
        while self.is_running:
            try:
                # Distribute collected data
                await self._distribute_collected_data()
                
                # Update feed status
                await self._update_feed_status()
                
                await asyncio.sleep(0.5)  # 500ms cycle
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in data distribution loop: {e}")
                await asyncio.sleep(5)
    
    # ============= DATA DISTRIBUTION OPERATIONS =============
    
    async def _distribute_collected_data(self):
        """Distribute collected data to subscribers."""
        try:
            # Distribute price updates
            if self.stats["price_updates"] > 0:
                await self._distribute_price_data()
            
            # Distribute sentiment updates
            if self.stats["sentiment_updates"] > 0:
                await self._distribute_sentiment_data()
            
            # Distribute order book updates
            if self.stats["order_book_updates"] > 0:
                await self._distribute_order_book_data()
            
            # Distribute derived data
            if self.stats["derived_data_updates"] > 0:
                await self._distribute_derived_data()
                
        except Exception as e:
            self.logger.error(f"Error distributing collected data: {e}")
    
    async def _update_feed_status(self):
        """Update feed status information."""
        try:
            current_time = time.time()
            
            # Update feed status
            for feed_type, monitor in self.feed_monitors.items():
                if monitor["status"] == "active":
                    monitor["last_update"] = current_time
                    monitor["update_count"] += 1
            
            # Update data feeds state
            self.data_feeds_state["last_data_update"] = current_time
            self.data_feeds_state["data_distribution_status"] = "active"
            
        except Exception as e:
            self.logger.error(f"Error updating feed status: {e}")
    
    async def _distribute_price_data(self):
        """Distribute price data to subscribers."""
        try:
            # Publish price updates to Redis
            if hasattr(self, 'redis_conn') and self.redis_conn:
                await self.redis_conn.publish_async(
                    self.data_channels["price_updates"],
                    json.dumps({
                        "timestamp": time.time(),
                        "feed_type": "price",
                        "update_count": self.stats["price_updates"]
                    })
                )
                
        except Exception as e:
            self.logger.error(f"Error distributing price data: {e}")
    
    async def _distribute_sentiment_data(self):
        """Distribute sentiment data to subscribers."""
        try:
            # Publish sentiment updates to Redis
            if hasattr(self, 'redis_conn') and self.redis_conn:
                await self.redis_conn.publish_async(
                    self.data_channels["sentiment_updates"],
                    json.dumps({
                        "timestamp": time.time(),
                        "feed_type": "sentiment",
                        "update_count": self.stats["sentiment_updates"]
                    })
                )
                
        except Exception as e:
            self.logger.error(f"Error distributing sentiment data: {e}")
    
    async def _distribute_order_book_data(self):
        """Distribute order book data to subscribers."""
        try:
            # Publish order book updates to Redis
            if hasattr(self, 'redis_conn') and self.redis_conn:
                await self.redis_conn.publish_async(
                    self.data_channels["order_book_updates"],
                    json.dumps({
                        "timestamp": time.time(),
                        "feed_type": "orderbook",
                        "update_count": self.stats["order_book_updates"]
                    })
                )
                
        except Exception as e:
            self.logger.error(f"Error distributing order book data: {e}")
    
    async def _distribute_derived_data(self):
        """Distribute derived data to subscribers."""
        try:
            # Publish derived data updates to Redis
            if hasattr(self, 'redis_conn') and self.redis_conn:
                await self.redis_conn.publish_async(
                    self.data_channels["derived_data"],
                    json.dumps({
                        "timestamp": time.time(),
                        "feed_type": "derived",
                        "update_count": self.stats["derived_data_updates"]
                    })
                )
                
        except Exception as e:
            self.logger.error(f"Error distributing derived data: {e}")
    
    # ============= MT5 DATA FETCHING =============
    
    async def _init_mt5_connection(self):
        """Initialize MT5 connection for data fetching."""
        try:
            # Try to import MT5 broker (optional for non-Windows systems)
            try:
                from engine_agents.adapters.brokers.mt5_plugin import MT5Broker
            except ImportError as ie:
                self.logger.warning(f"⚠️ MT5 plugin not available (likely running on non-Windows system): {ie}")
                self.stats["mt5_connection_status"] = "unavailable"
                return
            
            # Initialize MT5 adapter
            self.mt5_adapter = MT5Broker(
                login=self.config.get('mt5_login', 12345678),
                password=self.config.get('mt5_password', 'demo'),
                server=self.config.get('mt5_server', 'MetaQuotes-Demo')
            )
            
            # Connect to MT5
            self.mt5_adapter.connect()
            
            # Update connection status
            self.stats["mt5_connection_status"] = "connected"
            
            self.logger.info("✅ MT5 connection established")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing MT5 connection: {e}")
            self.stats["mt5_connection_status"] = "failed"
            # Don't raise - continue without MT5
            self.logger.warning("⚠️ Continuing without MT5 connection")
    
    def _init_core_price_feeds(self):
        """Initialize core price feeds."""
        try:
            # Initialize price feeds for different asset classes
            self.price_feeds = {
                "forex": {"status": "active", "symbols": []},
                "indices": {"status": "active", "symbols": []},
                "stocks": {"status": "active", "symbols": []},
                "energy": {"status": "active", "symbols": []},
                "crypto": {"status": "active", "symbols": []}
            }
            
            self.logger.info("✅ Core price feeds initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing core price feeds: {e}")
            raise
    
    def _init_streamlined_sentiment_feeds(self):
        """Initialize streamlined sentiment feeds."""
        try:
            # Initialize sentiment feeds
            self.sentiment_feeds = {
                "news_sentiment": {"status": "active", "sources": []},
                "social_sentiment": {"status": "active", "sources": []},
                "market_sentiment": {"status": "active", "indicators": []}
            }
            
            self.logger.info("✅ Streamlined sentiment feeds initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing sentiment feeds: {e}")
            raise
    
    def _init_strategy_order_book_feeds(self):
        """Initialize strategy order book feeds."""
        try:
            # Initialize order book feeds
            self.order_book_feeds = {
                "level1": {"status": "active", "depth": 1},
                "level2": {"status": "active", "depth": 5},
                "level3": {"status": "active", "depth": 10}
            }
            
            self.logger.info("✅ Strategy order book feeds initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing order book feeds: {e}")
            raise
    
    def _init_strategy_derived_data(self):
        """Initialize strategy derived data processors."""
        try:
            # Initialize derived data processors
            self.derived_data_processors = {
                "technical_indicators": {"status": "active", "indicators": []},
                "market_microstructure": {"status": "active", "metrics": []},
                "correlation_analysis": {"status": "active", "pairs": []}
            }
            
            self.logger.info("✅ Strategy derived data processors initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing derived data processors: {e}")
            raise
    
    # ============= MT5 DATA STREAMING =============
    
    async def _mt5_price_stream(self):
        """MT5 price streaming loop."""
        while self.is_running:
            try:
                if self.mt5_adapter and self.stats["mt5_connection_status"] == "connected":
                    # Fetch latest prices
                    await self._fetch_mt5_prices()
                    
                    # Update statistics
                    self.stats["price_updates"] += 1
                    self.stats["last_price_update"] = time.time()
                
                await asyncio.sleep(self.price_update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in MT5 price stream: {e}")
                await asyncio.sleep(5)
    
    async def _fetch_mt5_prices(self):
        """Fetch latest prices from MT5."""
        try:
            # Fetch prices for different asset classes
            for asset_class in self.mt5_symbols:
                if self.mt5_symbols[asset_class]:
                    # Fetch prices for this asset class
                    prices = await self.mt5_adapter.get_prices(self.mt5_symbols[asset_class])
                    
                    # Update statistics
                    self.stats[f"{asset_class}_updates"] += 1
                    
                    # Publish to Redis if available
                    if hasattr(self, 'redis_conn') and self.redis_conn:
                        await self.redis_conn.publish_async(
                            f"mt5:prices:{asset_class}",
                            json.dumps(prices)
                        )
                        
        except Exception as e:
            self.logger.error(f"Error fetching MT5 prices: {e}")
    
    async def _refresh_symbols_periodically(self):
        """Refresh MT5 symbols periodically."""
        while self.is_running:
            try:
                if self.mt5_adapter and self.stats["mt5_connection_status"] == "connected":
                    # Refresh symbols for all asset classes
                    await self._refresh_mt5_symbols()
                
                await asyncio.sleep(300)  # 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error refreshing symbols: {e}")
                await asyncio.sleep(600)  # 10 minutes on error
    
    async def _refresh_mt5_symbols(self):
        """Refresh MT5 symbols for all asset classes."""
        try:
            # Refresh forex symbols
            self.mt5_symbols["forex"] = await self.mt5_adapter.get_forex_symbols()
            
            # Refresh indices symbols
            self.mt5_symbols["indices"] = await self.mt5_adapter.get_indices_symbols()
            
            # Refresh stocks symbols
            self.mt5_symbols["stocks"] = await self.mt5_adapter.get_stocks_symbols()
            
            # Refresh energy symbols
            self.mt5_symbols["energy"] = await self.mt5_adapter.get_energy_symbols()
            
            # Refresh crypto symbols
            self.mt5_symbols["crypto"] = await self.mt5_adapter.get_crypto_symbols()
            
            # Refresh crypto cross symbols
            self.mt5_symbols["crypto_cross"] = await self.mt5_adapter.get_crypto_cross_symbols()
            
            self.logger.info("✅ MT5 symbols refreshed")
            
        except Exception as e:
            self.logger.error(f"Error refreshing MT5 symbols: {e}")
    
    def get_data_feeds_status(self) -> Dict[str, Any]:
        """Get data feeds status."""
        return {
            "agent_name": self.agent_name,
            "is_running": self.is_running,
            "mt5_connection": self.stats["mt5_connection_status"],
            "active_feeds": len([f for f in self.price_feeds.values() if f["status"] == "active"]),
            "total_updates": sum([
                self.stats["price_updates"],
                self.stats["sentiment_updates"],
                self.stats["order_book_updates"],
                self.stats["derived_data_updates"]
            ]),
            "last_update": self.stats["last_price_update"],
            "timestamp": time.time()
        } 