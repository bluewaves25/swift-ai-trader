Capital Exposure Control
The risk_management/ module enforces strict capital exposure limits to protect trading operations.
Exposure Limits

Per-Asset Limits: Caps exposure to individual assets (e.g., 10% of capital for BTC/USD).
Portfolio Limits: Restricts total portfolio exposure (e.g., 50% of capital across all assets).
Strategy Limits: Limits exposure per strategy (e.g., 20% for market-making).

Implementation

Monitored via strategy_specific/ components like InventoryControlRisk.
Real-time updates through Redis integration with Fee Monitor and Executions agents.
Violations trigger immediate notifications to execution_agent for position adjustments.

Dynamic Adjustments

Exposure limits adjust based on market volatility and liquidity signals.
GlobalLiquiditySignalRisk and RegimeShiftDetectorRisk inform limit recalibration.
Ensures resilience across Forex, Crypto, Indices, and Commodities.
