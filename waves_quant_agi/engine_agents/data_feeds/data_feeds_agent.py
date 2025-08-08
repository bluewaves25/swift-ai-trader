import asyncio
import time
from typing import Dict, Any, Optional, List
import redis
from .logs.data_feeds_logger import DataFeedsLogger
from .price.crypto_price_feed import CryptoPriceFeed
from .price.forex_price_feed import ForexPriceFeed
from .price.equities_price_feed import EquitiesPriceFeed
from .sentiment.twitter_sentiment import TwitterSentiment
from .sentiment.news_scraper import NewsScraper
from .sentiment.sentiment_aggregator import SentimentAggregator
from .order_book.binance_order_book import BinanceOrderBook
from .order_book.order_book_normalizer import OrderBookNormalizer
from .trade_tape.trade_collector import TradeCollector
from .trade_tape.trade_parser import TradeParser
from .derived_signals.indicators import Indicators
from .derived_signals.signal_generator import SignalGenerator
from .market_microstructure.microstructure_extractor import MicrostructureExtractor
from .market_microstructure.slippage_tracker import SlippageTracker
from .stream.realtime_publisher import RealtimePublisher
from .stream.realtime_subscriber import RealtimeSubscriber
from .cache.db_connector import DBConnector

class DataFeedsAgent:
    """Main orchestrator for all data feeds with real-time processing and distribution."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        
        # Initialize Redis connection
        self.redis_client = self._init_redis()
        self.logger = DataFeedsLogger("data_feeds_agent", self.redis_client)
        
        # Initialize core components
        self.db = DBConnector(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0)
        )
        self.publisher = RealtimePublisher(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0)
        )
        
        # Initialize price feeds
        self._init_price_feeds()
        
        # Initialize sentiment feeds
        self._init_sentiment_feeds()
        
        # Initialize order book feeds
        self._init_order_book_feeds()
        
        # Initialize trade tape feeds
        self._init_trade_tape_feeds()
        
        # Initialize derived signals
        self._init_derived_signals()
        
        # Initialize market microstructure
        self._init_market_microstructure()
        
        # Performance tracking
        self.stats = {
            "total_data_points": 0,
            "price_data_points": 0,
            "sentiment_data_points": 0,
            "order_book_data_points": 0,
            "trade_tape_data_points": 0,
            "derived_signals": 0,
            "microstructure_data": 0,
            "start_time": time.time(),
            "last_update": time.time()
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
            self.logger.log_error(f"Failed to initialize Redis: {e}")
            return None

    def _init_price_feeds(self):
        """Initialize price feed components."""
        try:
            # Crypto price feed
            crypto_config = self.config.get("crypto_price_feed", {
                "symbols": ["BTC/USDT", "ETH/USDT", "BNB/USDT"],
                "interval": 1,
                "exchanges": {
                    "binance": {"sandbox": False},
                    "coinbase": {"sandbox": False},
                    "kraken": {"sandbox": False}
                }
            })
            self.crypto_feed = CryptoPriceFeed(crypto_config)
            
            # Forex price feed
            forex_config = self.config.get("forex_price_feed", {
                "symbols": ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"],
                "interval": 1,
                "exchanges": {
                    "oanda": {"sandbox": False},
                    "fxcm": {"sandbox": False}
                }
            })
            self.forex_feed = ForexPriceFeed(forex_config)
            
            # Equities price feed (placeholder)
            self.equities_feed = None  # Will be implemented later
            
            self.logger.log("Price feeds initialized successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error initializing price feeds: {e}")

    def _init_sentiment_feeds(self):
        """Initialize sentiment feed components."""
        try:
            # Twitter sentiment
            twitter_config = self.config.get("twitter_sentiment", {
                "keywords": ["bitcoin", "crypto", "trading"],
                "interval": 60
            })
            self.twitter_sentiment = TwitterSentiment(twitter_config)
            
            # News scraper
            news_config = self.config.get("news_scraper", {
                "sources": ["reuters", "bloomberg", "cnbc"],
                "interval": 300
            })
            self.news_scraper = NewsScraper(news_config)
            
            # Sentiment aggregator
            sentiment_config = self.config.get("sentiment_aggregator", {
                "aggregation_interval": 60
            })
            self.sentiment_aggregator = SentimentAggregator(sentiment_config)
            
            self.logger.log("Sentiment feeds initialized successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error initializing sentiment feeds: {e}")

    def _init_order_book_feeds(self):
        """Initialize order book feed components."""
        try:
            # Binance order book
            order_book_config = self.config.get("order_book", {
                "symbols": ["BTC/USDT", "ETH/USDT"],
                "depth": 20,
                "interval": 1
            })
            self.binance_order_book = BinanceOrderBook(order_book_config)
            
            # Order book normalizer
            self.order_book_normalizer = OrderBookNormalizer()
            
            self.logger.log("Order book feeds initialized successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error initializing order book feeds: {e}")

    def _init_trade_tape_feeds(self):
        """Initialize trade tape feed components."""
        try:
            # Trade collector
            trade_config = self.config.get("trade_collector", {
                "symbols": ["BTC/USDT", "ETH/USDT"],
                "interval": 1
            })
            self.trade_collector = TradeCollector(trade_config)
            
            # Trade parser
            self.trade_parser = TradeParser()
            
            self.logger.log("Trade tape feeds initialized successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error initializing trade tape feeds: {e}")

    def _init_derived_signals(self):
        """Initialize derived signal components."""
        try:
            # Indicators
            indicators_config = self.config.get("indicators", {
                "indicators": ["sma", "ema", "rsi", "macd"],
                "periods": [14, 20, 50]
            })
            self.indicators = Indicators(indicators_config)
            
            # Signal generator
            signal_config = self.config.get("signal_generator", {
                "thresholds": {
                    "rsi_oversold": 30,
                    "rsi_overbought": 70,
                    "macd_signal": 0.001
                }
            })
            self.signal_generator = SignalGenerator(signal_config)
            
            self.logger.log("Derived signals initialized successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error initializing derived signals: {e}")

    def _init_market_microstructure(self):
        """Initialize market microstructure components."""
        try:
            # Microstructure extractor
            microstructure_config = self.config.get("microstructure", {
                "window_size": 100,
                "features": ["spread", "depth", "imbalance"]
            })
            self.microstructure_extractor = MicrostructureExtractor(microstructure_config)
            
            # Slippage tracker
            slippage_config = self.config.get("slippage_tracker", {
                "threshold": 0.001,
                "window_size": 50
            })
            self.slippage_tracker = SlippageTracker(slippage_config)
            
            self.logger.log("Market microstructure initialized successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error initializing market microstructure: {e}")

    async def start(self):
        """Start the data feeds agent."""
        try:
            self.logger.log("Starting Data Feeds Agent...")
            self.is_running = True
            
            # Start all feed tasks
            tasks = [
                asyncio.create_task(self._run_price_feeds()),
                asyncio.create_task(self._run_sentiment_feeds()),
                asyncio.create_task(self._run_order_book_feeds()),
                asyncio.create_task(self._run_trade_tape_feeds()),
                asyncio.create_task(self._run_derived_signals()),
                asyncio.create_task(self._run_market_microstructure()),
                asyncio.create_task(self._stats_reporting_loop())
            ]
            
            # Start all tasks
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logger.log_error(f"Error starting data feeds agent: {e}")
            await self.stop()

    async def stop(self):
        """Stop the data feeds agent gracefully."""
        self.logger.log("Stopping Data Feeds Agent...")
        self.is_running = False
        
        try:
            # Close all feeds
            if hasattr(self, 'crypto_feed'):
                await self.crypto_feed.close()
            if hasattr(self, 'forex_feed'):
                await self.forex_feed.close()
            
            self.publisher.close()
            self.db.close()
            
            self.logger.log("Data Feeds Agent stopped successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error stopping data feeds agent: {e}")

    async def _run_price_feeds(self):
        """Run price feed streams."""
        while self.is_running:
            try:
                # Start crypto price stream
                if hasattr(self, 'crypto_feed'):
                    await self.crypto_feed.stream_prices()
                
                # Start forex price stream
                if hasattr(self, 'forex_feed'):
                    await self.forex_feed.stream_prices()
                
            except Exception as e:
                self.logger.log_error(f"Error in price feeds: {e}")
                await asyncio.sleep(5)

    async def _run_sentiment_feeds(self):
        """Run sentiment feed streams."""
        while self.is_running:
            try:
                # Process sentiment feeds
                if hasattr(self, 'twitter_sentiment'):
                    await self.twitter_sentiment.process_sentiment()
                
                if hasattr(self, 'news_scraper'):
                    await self.news_scraper.scrape_news()
                
                if hasattr(self, 'sentiment_aggregator'):
                    await self.sentiment_aggregator.aggregate_sentiment()
                
                await asyncio.sleep(self.config.get("sentiment_interval", 60))
                
            except Exception as e:
                self.logger.log_error(f"Error in sentiment feeds: {e}")
                await asyncio.sleep(30)

    async def _run_order_book_feeds(self):
        """Run order book feed streams."""
        while self.is_running:
            try:
                # Process order book feeds
                if hasattr(self, 'binance_order_book'):
                    await self.binance_order_book.stream_order_book()
                
                await asyncio.sleep(self.config.get("order_book_interval", 1))
                
            except Exception as e:
                self.logger.log_error(f"Error in order book feeds: {e}")
                await asyncio.sleep(5)

    async def _run_trade_tape_feeds(self):
        """Run trade tape feed streams."""
        while self.is_running:
            try:
                # Process trade tape feeds
                if hasattr(self, 'trade_collector'):
                    await self.trade_collector.collect_trades()
                
                await asyncio.sleep(self.config.get("trade_tape_interval", 1))
                
            except Exception as e:
                self.logger.log_error(f"Error in trade tape feeds: {e}")
                await asyncio.sleep(5)

    async def _run_derived_signals(self):
        """Run derived signal processing."""
        while self.is_running:
            try:
                # Process derived signals
                if hasattr(self, 'indicators'):
                    await self.indicators.calculate_indicators()
                
                if hasattr(self, 'signal_generator'):
                    await self.signal_generator.generate_signals()
                
                await asyncio.sleep(self.config.get("derived_signals_interval", 10))
                
            except Exception as e:
                self.logger.log_error(f"Error in derived signals: {e}")
                await asyncio.sleep(10)

    async def _run_market_microstructure(self):
        """Run market microstructure processing."""
        while self.is_running:
            try:
                # Process market microstructure
                if hasattr(self, 'microstructure_extractor'):
                    await self.microstructure_extractor.extract_features()
                
                if hasattr(self, 'slippage_tracker'):
                    await self.slippage_tracker.track_slippage()
                
                await asyncio.sleep(self.config.get("microstructure_interval", 5))
                
            except Exception as e:
                self.logger.log_error(f"Error in market microstructure: {e}")
                await asyncio.sleep(10)

    async def _stats_reporting_loop(self):
        """Report statistics and metrics."""
        while self.is_running:
            try:
                await self._report_stats()
                await asyncio.sleep(self.config.get("stats_interval", 60))
                
            except Exception as e:
                self.logger.log_error(f"Error in stats reporting: {e}")
                await asyncio.sleep(30)

    async def _report_stats(self):
        """Report agent statistics."""
        try:
            uptime = time.time() - self.stats["start_time"]
            
            stats_report = {
                "uptime_seconds": uptime,
                "total_data_points": self.stats["total_data_points"],
                "price_data_points": self.stats["price_data_points"],
                "sentiment_data_points": self.stats["sentiment_data_points"],
                "order_book_data_points": self.stats["order_book_data_points"],
                "trade_tape_data_points": self.stats["trade_tape_data_points"],
                "derived_signals": self.stats["derived_signals"],
                "microstructure_data": self.stats["microstructure_data"],
                "data_points_per_second": self.stats["total_data_points"] / max(uptime, 1),
                "last_update": self.stats["last_update"],
                "timestamp": time.time()
            }
            
            # Store stats in Redis
            if self.redis_client:
                self.redis_client.hset("data_feeds:stats", mapping=stats_report)
            
            # Log metrics
            self.logger.log_metric("total_data_points", self.stats["total_data_points"])
            self.logger.log_metric("data_points_per_second", stats_report["data_points_per_second"])
            
        except Exception as e:
            self.logger.log_error(f"Error reporting stats: {e}")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        uptime = time.time() - self.stats["start_time"]
        
        return {
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "stats": self.stats,
            "components": {
                "crypto_feed": hasattr(self, 'crypto_feed') and self.crypto_feed is not None,
                "forex_feed": hasattr(self, 'forex_feed') and self.forex_feed is not None,
                "twitter_sentiment": hasattr(self, 'twitter_sentiment') and self.twitter_sentiment is not None,
                "news_scraper": hasattr(self, 'news_scraper') and self.news_scraper is not None,
                "binance_order_book": hasattr(self, 'binance_order_book') and self.binance_order_book is not None,
                "trade_collector": hasattr(self, 'trade_collector') and self.trade_collector is not None,
                "indicators": hasattr(self, 'indicators') and self.indicators is not None,
                "signal_generator": hasattr(self, 'signal_generator') and self.signal_generator is not None,
                "microstructure_extractor": hasattr(self, 'microstructure_extractor') and self.microstructure_extractor is not None,
                "slippage_tracker": hasattr(self, 'slippage_tracker') and self.slippage_tracker is not None
            }
        } 