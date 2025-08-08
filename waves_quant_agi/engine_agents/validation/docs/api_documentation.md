API Documentation
Overview
The Validators Agent exposes gRPC/REST APIs for validation requests, integrating with external systems and agents.
Endpoints

/validation/validate_trade (gRPC):
Input: ValidateTradeRequest { signal (string), size (float), symbol (string), entry_price (float), stop_loss (float), take_profit (float), timestamp (int64), region (string), leverage (float) }
Output: ValidateTradeResponse { status (string), reason (string), details (map<string, bool>) }
Description: Validates trade signals (router.rs).


/validation/validate_strategy (gRPC):
Input: ValidateStrategyRequest { symbol (string), strategy_type (string), entry_price (float), exit_price (float), timestamp (int64) }
Output: ValidateStrategyResponse { status (string), reason (string), details (map<string, bool>) }
Description: Validates strategy logic (strategy_filter.rs).


/validation/metrics (gRPC):
Input: ValidationMetricsRequest { }
Output: ValidationMetricsResponse { metrics (list of { symbol, error_rate, accuracy, timestamp }) }
Description: Retrieves validation metrics (audit_memory.py).



Integration

Rust-Python: PyO3 bridges Rust validators to Python learning layer (training_module.py).
External Systems: Inputs via validation_input Redis channel; outputs to validation_output.
Security: Requires authentication tokens from config.yaml.
Logging: Errors logged in validation:errors with 7-day expiry.

Usage

gRPC call: validate_trade(signal="BUY", size=100000, symbol="BTC/USD", entry_price=50000.0)
REST equivalent: POST /validate_trade with JSON payload.
