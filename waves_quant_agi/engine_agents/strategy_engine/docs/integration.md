Integration with Agents
Overview
The strategy engine integrates with Market Conditions, Executions, Risk Management, and Fee Monitor agents to enable adaptive trading across Forex, Crypto, Indices, and Commodities.
Integration Points
1. Market Conditions Agent

Role: Provides real-time market data (price, volatility, liquidity, sentiment).
Interface: Redis channel market_conditions_output.
Usage:
momentum_rider.py uses momentum and RSI for BTC/USD signals.
pairs_trading.py uses z-scores for ETH/BTC pair trading.


Data Flow: Market data ingested as pandas DataFrames or dicts.

2. Executions Agent

Role: Executes trades based on strategy signals.
Interface: Redis channel execution_agent.
Usage:
spread_adjuster.py sends adjusted spreads for EUR/USD.
agent_fusion_engine.py sends fused signals for S&P 500.


Data Flow: Signals (buy/sell/hold) published with asset and timestamp.

3. Risk Management Agent

Role: Validates signals against risk thresholds (e.g., position size, volatility).
Interface: Indirect via strategy_engine_output and Core Agent.
Usage:
volatility_responsive_mm.py checks volatility for Oil trades.
macro_trend_tracker.py aligns NAS 100 signals with risk profiles.


Data Flow: Risk parameters embedded in signal metadata.

4. Fee Monitor Agent

Role: Ensures cost-efficient trades.
Interface: Redis key fee_monitor:<symbol>:fee_score.
Usage:
latency_arbitrage.py compares price differences to fee_score for BTC/USD.
adaptive_quote.py adjusts quotes for ETH/USD based on fees.


Data Flow: Fee scores retrieved before signal execution.

Workflow

Market Conditions Agent pushes data to market_conditions_output.
Strategy engine processes data, generates signals (e.g., sentiment_analysis.py).
Signals validated by Risk Management via Core Agent.
Fee Monitor ensures profitability; signals sent to Executions Agent.
learning_layer (e.g., retraining_loop.py) refines strategies based on performance.

Robustness

FailureAgentLogger logs integration failures.
IncidentCache stores incidents for analysis (7-day expiry).

Scalability

Modular integration supports new assets (e.g., SOL/USD) and strategies.
Redis ensures high-throughput communication.
