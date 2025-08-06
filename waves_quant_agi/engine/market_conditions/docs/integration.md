Integration with Other Agents
Overview
The Quantum Supply-Demand Intelligence Agent integrates with other agents in the Waves Quant trading platform to provide real-time market insights. It processes data through market_conditions/learning_layer and quantum_core, publishing results to the Redis channel market_conditions_output for consumption by other components.
Integration Points

Core Agent:
Input: Receives fused signals, performance metrics, and anomaly alerts from market_conditions_output.
Usage: Uses outputs from q_interpreter.py (parallel hypotheses), entanglement_matrix.py (pattern convergence), and uncertainty_solver.py (resolved uncertainties) to inform trading strategies.
Example: Core Agent adjusts trade execution based on high-confidence trends from shift_predictor_fuser.py or anomaly alerts from social_sentiment_analyzer.py.


Fees Monitor Agent:
Input: Consumes volatility and equilibrium data from volatility_projector.py and market_equilibrium.py via Redis.
Usage: Optimizes transaction costs by aligning trades with low-volatility periods or stable equilibria.
Example: Avoids high-fee trades during chaotic patterns detected by entanglement_matrix.py.


Risk Management Agent:
Input: Subscribes to market_conditions_output for risk-related signals (e.g., risk_collapse_predictor.py, entropy_analyzer.py).
Usage: Mitigates exposure during high-entropy or risk-collapse scenarios.
Example: Reduces position sizes when uncertainty_solver.py flags unresolved market ambiguities.


Execution Agent:
Input: Uses optimized decisions from decision_optimizer.py and quantum_optimizer.py.
Usage: Executes trades based on actionable signals (e.g., buy/hold from trend_synthesizer.py).
Example: Triggers buy orders when quantum_pattern_recognizer.py detects a bullish pattern.



Technical Details

Redis Integration: All outputs (e.g., trends, anomalies, decisions) are cached in Redis with keys like market_conditions:trend:{symbol} (7-day expiration) for low-latency access.
Data Format: Outputs are JSON-serialized dictionaries with fields: type, symbol, score, timestamp, description.
Error Handling: Errors are logged via FailureAgentLogger and cached in IncidentCache, ensuring other agents receive error notifications.
Scalability: Configurable thresholds (e.g., trend_threshold, entropy_threshold) allow adaptation to new assets or markets.

Best Practices

Subscribe to market_conditions_output for real-time updates.
Cross-reference signals from multiple modules (e.g., social_sentiment_analyzer.py, global_event_monitor.py) for robust decisions.
Use cached data to reduce redundant processing, leveraging Redis expiration for freshness.
