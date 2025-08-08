Normalization Rules
Purpose
Ensure data consistency across feeds for compatibility with Core and Strategy Agents.
Rules

String Formatting:

Convert all strings to lowercase (DataCleaner).
Remove special characters, keep alphanumeric, spaces, and /- (DataCleaner).
Example: BTC/USDT → btcusdt.


Numeric Precision:

Round floats to 8 decimals for prices, volumes, and indicators (DataCleaner).
Example: 123.456789123 → 123.45678912.


Timestamps:

Use UTC timezone-aware timestamps (TimestampUtils).
Align to nearest second if needed (align_timestamp).
Example: 1698765432.123 → 1698765432.0.


Order Book:

Bids/asks as lists of [price, amount] pairs, floats rounded to 8 decimals (OrderBookNormalizer).
Example: [[1000.123456789, 1.23456789], ...] → [[1000.12345679, 1.23456789], ...].


Trade Tape:

Standardize side as lowercase "buy" or "sell" (TradeParser).
Ensure price and amount are floats (TradeParser).


Sentiment:

Sentiment scores normalized to -1.0 to 1.0 (TwitterSentiment, NewsScraper).
Truncate text fields to 500 characters (DataCleaner).


Microstructure:

Spread and liquidity as floats, rounded to 8 decimals (MicrostructureExtractor).
Slippage as a percentage, rounded to 8 decimals (SlippageTracker).


Schema Validation:

All data must conform to predefined schemas (SchemaValidator).
Required fields enforced (e.g., symbol, timestamp).



Implementation

DataCleaner: Handles string cleaning and numeric rounding.
TimestampUtils: Ensures consistent timestamp formatting.
SchemaValidator: Enforces schema compliance.
Specific normalizers (OrderBookNormalizer, TradeParser) handle module-specific rules.
