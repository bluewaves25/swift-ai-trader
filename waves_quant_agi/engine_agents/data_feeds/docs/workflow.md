Data Feed Agent Workflow
Overview
The Data Feed Agent operates in a streamlined pipeline to collect, process, and stream market data to Core and Strategy Agents, ensuring low-latency, clean, and reliable outputs.
Workflow Steps

Data Collection:

Fetch raw data from exchanges (e.g., Binance, Coinbase) via CryptoPriceFeed, ForexPriceFeed, EquitiesPriceFeed, BinanceOrderBook, and TradeCollector.
Scrape sentiment data from Twitter (TwitterSentiment) and news sources (NewsScraper).
Example: {"symbol": "BTCUSDT", "price": 50000.0, "volume": 10.0, "timestamp": 1234567890.0}.


Cleaning & Normalization:

Clean data using DataCleaner (remove special characters, round floats to 8 decimals).
Normalize formats with OrderBookNormalizer and TradeParser (e.g., lowercase strings, standardize symbols).
Validate against schemas with SchemaValidator.


Timestamping:

Apply UTC timezone-aware timestamps using TimestampUtils.get_timestamp().
Align timestamps to intervals if needed (align_timestamp).


Derived Signals:

Calculate indicators (e.g., RSI, VWAP) with Indicators.
Generate trading signals (e.g., buy/sell) with SignalGenerator based on indicators.


Microstructure Analysis:

Extract metrics like spread and liquidity with MicrostructureExtractor.
Track slippage with SlippageTracker using trade and order book data.


Streaming:

Publish data to Redis channels (e.g., "crypto_price", "trading_signal") via RealtimePublisher.
Other agents subscribe using RealtimeSubscriber.


Storage & Backfilling:

Store data in Redis with DBConnector.store() for archiving.
Backfill gaps using DBConnector.backfill() for training or analysis.


Learning Integration:

Analyze feed behavior with ResearchEngine.analyze_feed_behavior().
Prepare training datasets with TrainingModule.prepare_dataset().
Retrain periodically with RetrainingLoop.run_retraining().



Circular Nature
The workflow runs continuously, with data collection triggering processing, streaming, and storage. Insights from the learning layer feed back to optimize signal generation and data quality.
Diagram
graph TD
    A[Raw Data Collection] --> B[DataCleaner]
    B --> C[TimestampUtils]
    C --> D[SchemaValidator]
    D --> E[Indicators & SignalGenerator]
    D --> F[MicrostructureExtractor & SlippageTracker]
    E --> G[RealtimePublisher]
    F --> G
    G --> H[DBConnector]
    H --> I[ResearchEngine]
    I --> J[TrainingModule]
    J --> K[RetrainingLoop]
    K --> E
    H --> G[RealtimePublisher]
