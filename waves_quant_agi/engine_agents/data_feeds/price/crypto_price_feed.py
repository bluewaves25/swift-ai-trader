import asyncio
import ccxt.async_support as ccxt
from typing import Dict, Any, Optional, List
import time
from ..logs.data_feeds_logger import DataFeedsLogger
from ..utils.data_cleaner import DataCleaner
from ..utils.timestamp_utils import TimestampUtils
from ..utils.schema_validator import SchemaValidator
from ..stream.realtime_publisher import RealtimePublisher
from ..cache.db_connector import DBConnector

class CryptoPriceFeed:
    """Real-time cryptocurrency price feed with multiple exchange support."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.exchanges = {}
        self.symbols = config.get("symbols", ["BTC/USDT", "ETH/USDT", "BNB/USDT"])
        self.interval = config.get("interval", 1)  # seconds
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 5)  # seconds
        
        # Initialize components
        self.redis_client = self._init_redis()
        self.logger = DataFeedsLogger("crypto_price_feed", self.redis_client)
        self.cleaner = DataCleaner()
        self.timestamp_utils = TimestampUtils()
        self.validator = SchemaValidator()
        self.publisher = RealtimePublisher(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0)
        )
        self.db = DBConnector(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0)
        )
        
        # Initialize exchanges
        self._init_exchanges()
        
        # Performance tracking
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "last_update": time.time(),
            "start_time": time.time()
        }
        
        self.schema = {
            "exchange": str,
            "symbol": str,
            "price": float,
            "volume": float,
            "timestamp": float,
            "bid": float,
            "ask": float,
            "high": float,
            "low": float
        }

    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            import redis
            return redis.Redis(
                host=self.config.get("redis_host", "localhost"),
                port=self.config.get("redis_port", 6379),
                db=self.config.get("redis_db", 0),
                decode_responses=True
            )
        except Exception as e:
            self.logger.log_error(f"Failed to initialize Redis: {e}")
            return None

    def _init_exchanges(self):
        """Initialize exchange connections."""
        exchange_configs = self.config.get("exchanges", {
            "binance": {"sandbox": False},
            "coinbase": {"sandbox": False},
            "kraken": {"sandbox": False}
        })
        
        for exchange_name, config in exchange_configs.items():
            try:
                exchange_class = getattr(ccxt, exchange_name)
                exchange = exchange_class(config)
                self.exchanges[exchange_name] = exchange
                self.logger.log_connection_status(exchange_name, "initialized")
            except Exception as e:
                self.logger.log_error(f"Failed to initialize {exchange_name}: {e}")

    async def fetch_price(self, exchange_name: str, exchange: ccxt.Exchange, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch price and volume for a symbol from an exchange with retry logic."""
        for attempt in range(self.max_retries):
            try:
                # Check if exchange is loaded
                if not exchange.has.get('fetchTicker', False):
                    self.logger.log_warning(f"{exchange_name} does not support fetchTicker")
                    return None
                
                ticker = await exchange.fetch_ticker(symbol)
                
                # Validate ticker data
                if not ticker or 'last' not in ticker:
                    self.logger.log_warning(f"Invalid ticker data from {exchange_name} for {symbol}")
                    return None
                
                data = {
                    "exchange": exchange_name,
                    "symbol": symbol,
                    "price": float(ticker["last"]),
                    "volume": float(ticker.get("baseVolume", 0.0)),
                    "timestamp": self.timestamp_utils.get_timestamp(),
                    "bid": float(ticker.get("bid", 0.0)),
                    "ask": float(ticker.get("ask", 0.0)),
                    "high": float(ticker.get("high", 0.0)),
                    "low": float(ticker.get("low", 0.0))
                }
                
                # Validate and clean data
                if self.validator.validate(data, self.schema):
                    cleaned_data = self.cleaner.clean(data)
                    
                    # Log data point
                    self.logger.log_data_point(
                        "price", symbol, exchange_name, 
                        cleaned_data["price"],
                        {"volume": cleaned_data["volume"], "bid": cleaned_data["bid"], "ask": cleaned_data["ask"]}
                    )
                    
                    # Update stats
                    self.stats["successful_requests"] += 1
                    self.stats["last_update"] = time.time()
                    
                    return cleaned_data
                else:
                    self.logger.log_warning(f"Data validation failed for {symbol} on {exchange_name}")
                    return None
                    
            except ccxt.NetworkError as e:
                self.logger.log_warning(f"Network error fetching {symbol} from {exchange_name} (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                continue
                
            except ccxt.ExchangeError as e:
                self.logger.log_error(f"Exchange error fetching {symbol} from {exchange_name}: {e}")
                return None
                
            except Exception as e:
                self.logger.log_error(f"Unexpected error fetching {symbol} from {exchange_name}: {e}")
                return None
        
        self.stats["failed_requests"] += 1
        self.logger.log_error(f"Failed to fetch {symbol} from {exchange_name} after {self.max_retries} attempts")
        return None

    async def stream_prices(self):
        """Stream prices for all symbols and exchanges with error handling."""
        self.logger.log(f"Starting price stream for {len(self.symbols)} symbols on {len(self.exchanges)} exchanges")
        
        while True:
            try:
                start_time = time.time()
                tasks = []
                
                # Create tasks for all exchange-symbol combinations
                for exchange_name, exchange in self.exchanges.items():
                    for symbol in self.symbols:
                        tasks.append(self.fetch_price(exchange_name, exchange, symbol))
                
                # Execute all tasks concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                successful_data = []
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        self.logger.log_error(f"Task failed: {result}")
                        self.stats["failed_requests"] += 1
                    elif result:
                        successful_data.append(result)
                        self.stats["successful_requests"] += 1
                
                # Publish and store successful data
                for data in successful_data:
                    try:
                        self.publisher.publish("crypto_price", data)
                        self.db.store(data)
                    except Exception as e:
                        self.logger.log_error(f"Error publishing/storing data: {e}")
                
                # Log performance metrics
                processing_time = time.time() - start_time
                self.logger.log_metric("processing_time", processing_time)
                self.logger.log_metric("successful_requests", self.stats["successful_requests"])
                self.logger.log_metric("failed_requests", self.stats["failed_requests"])
                
                # Calculate success rate
                total_requests = self.stats["successful_requests"] + self.stats["failed_requests"]
                if total_requests > 0:
                    success_rate = (self.stats["successful_requests"] / total_requests) * 100
                    self.logger.log_metric("success_rate", success_rate)
                
                # Wait for next iteration
                await asyncio.sleep(self.interval)
                
            except Exception as e:
                self.logger.log_error(f"Error in price stream loop: {e}")
                await asyncio.sleep(self.interval)

    async def close(self):
        """Close all exchange connections gracefully."""
        self.logger.log("Closing crypto price feed...")
        
        try:
            for exchange_name, exchange in self.exchanges.items():
                try:
                    await exchange.close()
                    self.logger.log_connection_status(exchange_name, "closed")
                except Exception as e:
                    self.logger.log_error(f"Error closing {exchange_name}: {e}")
            
            self.publisher.close()
            self.logger.log("Crypto price feed closed successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error closing crypto price feed: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics."""
        uptime = time.time() - self.stats["start_time"]
        total_requests = self.stats["successful_requests"] + self.stats["failed_requests"]
        
        return {
            "uptime_seconds": uptime,
            "total_requests": total_requests,
            "successful_requests": self.stats["successful_requests"],
            "failed_requests": self.stats["failed_requests"],
            "success_rate": (self.stats["successful_requests"] / max(total_requests, 1)) * 100,
            "requests_per_second": total_requests / max(uptime, 1),
            "last_update": self.stats["last_update"],
            "active_exchanges": len(self.exchanges),
            "active_symbols": len(self.symbols)
        }