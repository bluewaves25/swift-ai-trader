Data Latency Considerations
Objective
Minimize latency in data collection, processing, and streaming to ensure timely delivery to Core and Strategy Agents.
Latency Sources

Data Collection:

Exchange API rate limits (e.g., ccxt for price, order book, trades).
Network delays for external APIs (e.g., NewsAPI, Twitter).
Example: Binance API may introduce 10-50ms latency per request.


Processing:

Cleaning (DataCleaner): ~1-5ms for string and numeric operations.
Normalization (OrderBookNormalizer, TradeParser): ~2-10ms for order book/trade data.
Indicator calculations (Indicators): ~5-20ms for RSI, VWAP.
Signal generation (SignalGenerator): ~5-15ms for rule-based signals.


Streaming:

Redis publish/subscribe (RealtimePublisher, RealtimeSubscriber): ~1-5ms for local Redis.
Network latency to other agents: ~5-50ms depending on infrastructure.


Storage:

Redis storage (DBConnector): ~1-10ms per write.
Backfilling queries: ~10-100ms depending on dataset size.



Mitigation Strategies

Asynchronous Processing: Use asyncio for concurrent data fetching (CryptoPriceFeed, ForexPriceFeed, etc.).
Batching: Fetch multiple symbols in parallel (stream_prices, stream_trades).
Caching: Store recent data in Redis for quick access (DBConnector).
Rate Limit Handling: Configure ccxt with enableRateLimit=True and respect API limits.
Efficient Normalization: Minimize regex and string operations in DataCleaner.
Prioritized Streaming: Use Redis channels with priority for critical data (e.g., prices over sentiment).
Monitoring: Log latency metrics in Redis for analysis by ResearchEngine.

Typical Latency Targets

End-to-end (collection to streaming): <100ms for price/trade data.
Sentiment data: <500ms due to external API constraints.
Microstructure metrics: <200ms for order book processing.

Example Monitoring
from data_feeds.utils.timestamp_utils import TimestampUtils
from data_feeds.cache.db_connector import DBConnector

ts = TimestampUtils()
db = DBConnector()
start = ts.get_timestamp()
# Fetch and process data
data = {"symbol": "BTCUSDT", "price": 50000.0, "timestamp": ts.get_timestamp()}
db.store(data)
latency = ts.get_timestamp() - start
db.store({"type": "latency", "value": latency, "timestamp": ts.get_timestamp()})
