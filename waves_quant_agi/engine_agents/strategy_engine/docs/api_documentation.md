API Documentation
Overview
The Quantum Supply-Demand Intelligence Agent's strategy engine exposes interfaces for interaction with internal components and external agents (Market Conditions, Executions, Risk Management, Fee Monitor). These interfaces support trading across Forex, Crypto, Indices, and Commodities.
Key Interfaces
1. Strategy Execution

Endpoint: Redis channel strategy_engine_output
Description: Publishes strategy signals (buy/sell/hold) to the Core Agent.
Payload:{
  "type": "<strategy_type>",
  "symbol": "<asset_symbol>",
  "signal": "<buy|sell|hold>",
  "timestamp": <unix_timestamp>,
  "description": "<signal_description>"
}


Examples:
latency_arbitrage.py: Publishes arbitrage opportunities for BTC/USD.
momentum_rider.py: Publishes momentum signals for NAS 100.



2. Execution Notification

Endpoint: Redis channel execution_agent
Description: Sends strategy signals to the Executions Agent for trade execution.
Payload: Same as strategy_engine_output.
Examples:
pairs_trading.py: Notifies buy/sell for ETH/BTC pair.
fed_policy_detector.py: Notifies signals for USD/JPY.



3. Training Interface

Endpoint: Redis channel training_module
Description: Sends failure patterns and research insights to training_module.py.
Payload:{
  "type": "<failure_pattern|research_insight>",
  "strategy_id": "<strategy_id>",
  "symbol": "<asset_symbol>",
  "timestamp": <unix_timestamp>,
  "description": "<pattern_description>"
}


Examples:
research_engine.py: Sends failure patterns for mean_reversion.py.
ai_lab_scraper.py: Sends research insights for strategy enhancement.



4. Market Data Input

Endpoint: Redis channel market_conditions_output
Description: Receives market data from Market Conditions Agent.
Payload:{
  "symbol": "<asset_symbol>",
  "price": <float>,
  "volatility": <float>,
  "liquidity_score": <float>,
  "sentiment_score": <float>,
  ...
}


Examples:
Used by volatility_responsive_mm.py for EUR/USD spread adjustments.
Used by global_liquidity_signal.py for Gold signals.



Configuration

Redis: Host (localhost), Port (6379), DB (0), configurable via config dict.
Thresholds: Strategy-specific (e.g., momentum_threshold, fusion_threshold).

Error Handling

Errors logged via FailureAgentLogger.
Incidents stored in IncidentCache with 7-day expiry.
Example: orchestration_trainer.py logs training errors.

Scalability

Modular interfaces support new strategies (e.g., regime_shift_detector.py).
Redis ensures low-latency communication across agents.
