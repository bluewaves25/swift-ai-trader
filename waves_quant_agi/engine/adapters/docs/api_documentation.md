API Documentation
Internal API Specifications
Order Format
The internal order format is standardized by OrderNormalizer for consistency across brokers:

Fields:
base: String, base currency (e.g., "BTC").
quote: String, quote currency (e.g., "USDT").
side: String, "buy" or "sell".
type: String, "market" or "limit".
amount: Float, order quantity.
price: Float, optional, price for limit orders.



Key Components

BrokerRouter:
select_broker(order): Selects optimal broker based on strategy.
route_order(order): Routes order to selected broker.
set_strategy(strategy_name): Sets routing strategy ("lowest_fee" or "fastest_route").


OrderNormalizer:
normalize(order, broker_name): Converts order to standard format.
validate(order): Validates order format.


HealthChecker:
check_broker(broker_name, adapter): Checks broker health.
monitor(): Continuously monitors all brokers.
get_status(broker_name): Returns broker status.


RetryHandler:
execute_with_retry(func, *args, **kwargs): Executes function with retries.
adjust_retry_params(success_rate): Adjusts retry settings.


PatternAnalyzer:
log_failure(broker_name, error, order): Logs failure event.
analyze_patterns(broker_name): Analyzes failure patterns.


BrokerIntelligence:
update_recommendations(broker_name, metrics): Updates broker recommendations.
get_recommendations(broker_name): Returns recommendations.


APIMonitor:
check_api_updates(): Monitors broker API changes.
notify_update(broker_name, new_version): Notifies of API changes.



Broker API Specifications
Binance

Library: ccxt.async_support.binance
Order Format:
symbol: String, e.g., "BTCUSDT".
side: String, "BUY" or "SELL".
type: String, "MARKET" or "LIMIT".
quantity: Float, rounded to 8 decimals.
price: Float, optional, rounded to 8 decimals.


Endpoints:
Order creation: client.create_order()
Order status: client.fetch_order(order_id)


Quirks:
Decimal precision: 8 for quantity and price.
Rate limits: Handled by ccxt with enableRateLimit.



Coinbase

Library: ccxt.async_support.coinbasepro
Order Format:
symbol: String, e.g., "BTC-USDT".
side: String, "buy" or "sell".
type: String, "market" or "limit".
size: Float, rounded to 6 decimals.
price: Float, optional, rounded to 6 decimals.


Endpoints:
Order creation: client.create_order()
Order status: client.fetch_order(order_id)


Quirks:
Decimal precision: 6 for size and price.
Rate limits: Handled by ccxt with enableRateLimit.



Exness

Library: requests
Order Format:
instrument: String, e.g., "BTCUSD".
side: String, "buy" or "sell".
type: String, "market" or "limit".
volume: Float, rounded to 4 decimals.
price: Float, optional, rounded to 5 decimals.


Endpoints:
Order creation: POST /v2/orders
Order status: GET /v2/orders/{order_id}


Quirks:
Volume precision: 4 decimals.
Price precision: 5 decimals.
Authentication: Bearer token with api_key:api_secret.



Notes

All brokers use BrokerLogger for request and error logging.
API changes are monitored by APIMonitor using broker documentation URLs.
Extend BaseAdapter for new brokers and update this file accordingly.
