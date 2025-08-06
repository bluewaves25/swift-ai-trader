API Reference
Internal API Specifications
Price Feeds

CryptoPriceFeed, ForexPriceFeed, EquitiesPriceFeed:
fetch_price(exchange_name, exchange, symbol): Returns {"exchange": str, "symbol": str, "price": float, "volume": float, "timestamp": float}.
stream_prices(): Streams price data to "crypto_price", "forex_price", or "equities_price".
close(): Closes exchange connections.



Sentiment

TwitterSentiment:
fetch_sentiment(keyword): Returns {"source": str, "keyword": str, "sentiment": float, "text": str, "timestamp": float}.
stream_sentiment(): Streams to "twitter_sentiment".


NewsScraper:
fetch_news(source, keyword): Returns {"source": str, "keyword": str, "sentiment": float, "title": str, "timestamp": float}.
stream_news(): Streams to "news_sentiment".


SentimentAggregator:
aggregate(data): Returns {"keyword": str, "aggregate_sentiment": float, "sources": list, "timestamp": float}.
stream_aggregated_sentiment(): Streams to "aggregated_sentiment".



Order Book

BinanceOrderBook:
fetch_order_book(symbol): Returns {"exchange": str, "symbol": str, "bids": list, "asks": list, "timestamp": float}.
stream_order_book(): Streams to "order_book".


OrderBookNormalizer:
normalize(order_book): Normalizes order book data.
process_and_publish(order_book): Streams to "normalized_order_book".



Trade Tape

TradeCollector:
fetch_trades(exchange_name, exchange, symbol): Returns {"exchange": str, "symbol": str, "price": float, "amount": float, "side": str, "timestamp": float}.
stream_trades(): Streams to "trade_tape".


TradeParser:
parse_trade(trade): Normalizes trade data.
process_and_publish(trade): Streams to "parsed_trade_tape".



Derived Signals

Indicators:
calculate_rsi(prices): Returns RSI value.
calculate_vwap(prices, volumes): Returns VWAP value.
process_indicators(data, price_history, volume_history): Streams to "indicator".


SignalGenerator:
generate_signal(indicators): Returns {"symbol": str, "signal_type": str, "strength": float, "timestamp": float}.
process_and_publish(indicators): Streams to "trading_signal".



Market Microstructure

MicrostructureExtractor:
extract_metrics(order_book): Returns {"symbol": str, "spread": float, "liquidity": float, "timestamp": float}.
process_and_publish(order_book): Streams to "microstructure".


SlippageTracker:
calculate_slippage(trade, order_book): Returns {"symbol": str, "slippage": float, "order_size": float, "timestamp": float}.
process_and_publish(trade, order_book): Streams to "slippage".



Utilities

DataCleaner:
clean(data): Returns cleaned data with normalized strings and floats.


TimestampUtils:
get_timestamp(timezone): Returns UTC timestamp.
align_timestamp(timestamp, interval): Aligns timestamp to interval.


SchemaValidator:
validate(data, schema): Returns bool for schema compliance.



Cache

DBConnector:
store(data): Stores data in Redis.
retrieve(key_pattern): Retrieves data by key pattern.
backfill(key_pattern, limit): Returns list of data for backfilling.



Stream

RealtimePublisher:
publish(channel, data): Publishes to Redis channel.
close(): Closes Redis connection.


RealtimeSubscriber:
subscribe(channels, callback): Subscribes to channels with callback.
stop(): Stops subscription.
close(): Closes Redis connection.



Learning Layer

ResearchEngine:
analyze_feed_behavior(key_pattern): Returns analysis of feed behavior.
collect_training_data(key_pattern): Returns data for training.


TrainingModule:
prepare_dataset(key_pattern): Returns dataset for training.
train_model(dataset): Returns training metrics.


RetrainingLoop:
run_retraining(): Runs periodic retraining.



External Agent Integration

Core Agent: Subscribes to Redis channels (e.g., "crypto_price", "trading_signal") via AgentIO.
Strategy Agent: Consumes signals and microstructure data for strategy decisions.
Channels: Use RealtimePublisher channels for data delivery.
