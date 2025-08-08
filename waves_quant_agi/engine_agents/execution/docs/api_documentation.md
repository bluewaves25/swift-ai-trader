API Documentation
The QUANTUM_AGENTS Execution Agent provides APIs for Rust-Python and external system integration, using gRPC/REST via api_bridge.rs.
Endpoints

/execution/execute_trade (gRPC):
Input: ExecuteTradeRequest { signal (string, e.g., "BUY"), size (float), symbol (string, e.g., "BTC/USD"), expected_price (float) }
Output: ExecuteTradeResponse { status (string, e.g., "success") }
Description: Triggers trade execution via order_executor.rs.


/execution/update_params (gRPC):
Input: UpdateParamsRequest { symbol (string), slippage_bps (float), max_latency_ms (float) }
Output: UpdateParamsResponse { status (string) }
Description: Updates execution parameters (e.g., slippage limits) from Python.


/execution/metrics (gRPC):
Input: ExecutionMetricsRequest { }
Output: ExecutionMetricsResponse { metrics (list of { symbol, latency, slippage_bps, timestamp }) }
Description: Retrieves execution metrics for Python analysis.



Integration

Rust-Python: PyO3 exposes execute_trade and update_params to Python (rust_data_collector.py).
External Systems: Communicates via Redis (execution_output, execution_logic) with Market Conditions and Fee Monitor.
Security: APIs require authentication tokens from config.yaml.
Logging: All requests logged in Redis (execution:errors) with 7-day expiry.

Usage

Python calls: from execution import execute_trade; execute_trade("BUY", 100000, "BTC/USD", 50000.0)
External systems publish signals to execution_logic Redis channel.
