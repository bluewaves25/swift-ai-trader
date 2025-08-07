Integration
The QUANTUM_AGENTS Execution Agent integrates with external systems (e.g., Strategy Engine, Market Conditions, Fee Monitor) to ensure seamless execution while maintaining independence.
Integration Points

Redis Channels:
Input: execution_logic receives trade signals (e.g., { "signal": "BUY", "size": 100000, "symbol": "BTC/USD", "expected_price": 50000.0 }).
Output: execution_output publishes execution results, metrics, and alerts.
Expiry: Data stored with 7-day expiry for efficiency.


Broker Connectivity: broker_interface.rs connects to brokers (e.g., Binance, OANDA) via APIs, configurable in config.yaml.
Python Feedback: learning_layer/ sends parameter updates (e.g., slippage limits) via PyO3 to execution_logic.rs.
Metrics Sharing: Execution metrics (latency, slippage) shared via execution:metric:* Redis keys for external analysis.

Setup

Configure Redis in config.yaml (redis_host, redis_port, redis_db).
Define broker endpoints and credentials in config.yaml.
Build PyO3 bindings with maturin develop.
Ensure external systems publish to execution_logic channel.

Error Handling

Broker failures trigger retries in order_executor.rs.
Invalid signals logged to execution:errors with descriptions.
Low confidence or stability alerts published to execution_output.

Scalability

Supports multiple brokers via broker_interface.rs.
Scales horizontally with additional execution/ instances.
Python layer scales with GPU clusters for training.
