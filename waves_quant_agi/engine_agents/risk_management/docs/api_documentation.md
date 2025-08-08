API Documentation
The risk_management/ module provides APIs for integration with Waves Quant components.
Endpoints

/risk/evaluate: Evaluates strategy-specific risks (e.g., MacroTrendTrackerRisk, RegimeShiftDetectorRisk).
Input: JSON with strategy, symbol, data (e.g., trend strength, volatility).
Output: JSON with decision, description, timestamp.


/risk/stress_test: Runs stress tests via StressTestRunner.
Input: JSON with scenarios, symbols.
Output: JSON with results, visuals_path.


/risk/entropy: Computes entropy via QuantumMonteCarlo.
Input: JSON with symbol, price_changes.
Output: JSON with entropy, description.


/risk/retrain: Triggers retraining via RetrainingLoop.
Input: JSON with risk_type, incident_data.
Output: JSON with trigger_status, timestamp.



Integration

APIs communicate via Redis channels (execution_agent, risk_management_output).
Data stored with 1-hour to 7-day expiry based on context.
Secured with authentication tokens (configured in config).

Usage

Called by Executions and Market Conditions agents.
Supports Forex, Crypto, Indices, and Commodities.
Logs interactions via FailureAgentLogger for auditability.
