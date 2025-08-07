Coordination Models
Overview
The Validators Agent integrates with other QUANTUM_AGENTS components (Strategy, Execution, Market Conditions, Fee Monitor) via Redis for loose coupling and independence.
Communication

Input Channel: validation_input (Redis pub/sub) receives JSON payloads from Strategy, Execution, or Backtest engines.
Example: { "signal": "BUY", "size": 100000, "symbol": "BTC/USD", "timestamp": 1697051234 }


Output Channel: validation_output publishes verdicts.
Example: { "status": "valid", "reason": "All checks passed", "details": { "timestamp_check": true } }


Error Logging: Failures stored in validation:errors with 7-day expiry.
Feedback: Learning layer publishes rule updates to retraining_loop and insights to agent_fusion_engine.

Integration Points

Strategy Agent: Sends strategy signals for validation.
Execution Agent: Receives validated inputs or rejection reasons.
Market Conditions Agent: Provides liquidity and volatility data via market:depth:* and market:timestamp:*.
Fee Monitor Agent: Supplies commission and slippage data via broker:commission:* and market:slippage:*.
Orchestration Layer: Monitors metrics via validation:audit_summary and validation:prediction_summary.

Workflow

Strategy Agent publishes signals to validation_input.
Validators Agent processes signals through orchestrator.rs.
Valid signals are forwarded to Execution Agent; rejections logged.
Learning layer analyzes outcomes, updating rules via PyO3 to Rust.

Independence

Validates inputs without fetching external data.
No assumptions about upstream agents; re-validates everything.
Can halt pipeline for severe violations (e.g., compliance breaches).
