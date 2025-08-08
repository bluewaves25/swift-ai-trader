Data Feed Agent Overview
Mission
The Data Feed Agent collects, preprocesses, and streams diverse market data to the Core, Strategy, and other agents, adhering to the principle "Intelligence without data is ignorance." It ensures clean, reliable, timestamped data without executing trades or making decisions.
Behavior

Data Collection: Gathers price, volume, order book, trade tape, sentiment, and microstructure data.
Cleaning & Normalization: Removes noise, aligns formats, and deduplicates using DataCleaner.
Timestamping: Ensures precise, timezone-aware timestamps via TimestampUtils.
Streaming: Pushes data to agents via RealtimePublisher using Redis.
Derived Signals: Calculates indicators (e.g., RSI, VWAP) and signals via Indicators and SignalGenerator.
Microstructure: Extracts metrics like spread and liquidity via MicrostructureExtractor and SlippageTracker.
Storage & Backfilling: Archives data and fills gaps using DBConnector (Redis).

Dependencies

External Libraries:
ccxt.async_support: For price, order book, and trade data.
tweepy: For Twitter sentiment.
requests: For news scraping.
redis: For streaming and caching.
numpy: For indicator calculations.
pytz: For timezone-aware timestamps.


Internal Modules:
price/: Crypto, forex, equities price feeds.
sentiment/: Twitter, news, and aggregated sentiment.
order_book/: Binance order book and normalization.
trade_tape/: Trade collection and parsing.
derived_signals/: Indicators and signal generation.
market_microstructure/: Spread, liquidity, and slippage tracking.
utils/: Cleaning, timestamping, and validation.
cache/: Redis-based storage.
stream/: Real-time publishing and subscribing.
learning_layer/: Research, training, and retraining.



Scalability

Modular design allows enabling/disabling modules for asset classes.
Redis ensures low-latency streaming and storage.
RetrainingLoop adapts to new data patterns.
SchemaValidator ensures data consistency across feeds.
