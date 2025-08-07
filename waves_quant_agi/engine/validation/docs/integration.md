Integration Guide
Overview
The Validators Agent integrates with QUANTUM_AGENTS components (Strategy, Execution, Market Conditions, Fee Monitor) via Redis pub/sub channels, ensuring loose coupling and independence.
Integration Points

Strategy Agent:
Input: Publishes strategy signals to validation_input (e.g., { "signal": "BUY", "symbol": "BTC/USD", "entry_price": 50000.0 }).
Output: Receives validation verdicts from validation_output.


Execution Agent:
Input: Receives validated signals via mpsc channel from orchestrator.rs.
Output: Sends execution feedback to validation:feedback:* for learning layer.


Market Conditions Agent:
Input: Provides liquidity/depth (market:depth:*) and timestamps (market:timestamp:*) via Redis.
Output: No direct output; Validators Agent queries data for validation.


Fee Monitor Agent:
Input: Supplies commission (broker:commission:*) and slippage (market:slippage:*) data.
Output: No direct output; used by cost_analysis.rs.


Learning Layer:
Input: Consumes failures (validation:failures:*) and audits (validation:audit:*).
Output: Publishes rule updates to retraining_loop and insights to agent_fusion_engine.



Communication

Redis Channels:
validation_input: Receives JSON payloads from upstream agents.
validation_output: Publishes verdicts (e.g., { "status": "valid", "reason": "All checks passed" }).
validation:errors: Logs rejections with 7-day expiry.
validation:audit:*: Stores validation metrics for learning.


gRPC/REST APIs:
Endpoints: /validate_trade, /validate_strategy, /validation/metrics.
Secured with authentication tokens from config.yaml.



Setup

Dependencies: Redis (redis://localhost:6379), Rust (Tokio, serde), Python (pandas, sklearn).
Configuration: Load config.yaml for thresholds (e.g., max_leverage, min_sl_ratio).
Startup: Run main.rs to initialize orchestrator.rs and listen on validation_input.

Error Handling

Rejections logged to validation:errors with detailed reasons.
Learning layer (research_engine.py) analyzes errors for rule refinement.
Critical failures (e.g., compliance breaches) halt pipeline via orchestrator.rs.
