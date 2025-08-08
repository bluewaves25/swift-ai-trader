Stress Testing Design
The simulation_engine/ within risk_management/ conducts stress tests to evaluate portfolio resilience.
Components

StressTestRunner: Executes historical and synthetic stress tests (e.g., market crashes, volatility spikes).
ScenarioBuilder: Generates adverse scenarios like black swans or liquidity drops.
OutcomeVisualizer: Visualizes test results for transparency.
RecoveryAnalyzer: Quantifies recovery times post-stress.

Methodology

Tests cover extreme market conditions across Forex, Crypto, Indices, and Commodities.
Scenarios simulate 10-20% price drops, 50% volatility spikes, and liquidity reductions.
Results stored in Redis with a 7-day expiry for analysis.

Integration

Interacts with market_conditions/ for real-time data.
Notifies execution_agent for failed tests to adjust positions.
Visuals saved in stress_test_visuals/ for stakeholder review.
