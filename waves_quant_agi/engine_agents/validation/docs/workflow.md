Validation Workflow
Overview
The Validators Agent orchestrates validation through a sequential pipeline, ensuring all inputs pass rigorous checks before reaching the Execution Agent.
Stages

Data Validation (router.rs):
Checks timestamp freshness (<60s).
Verifies data integrity (no NaN, missing fields).
Ensures source authenticity and no duplicates.


Risk Validation (risk_assessor.rs, stop_loss_checker.rs):
Confirms leverage ≤ max_leverage (default: 10x).
Ensures portfolio exposure ≤ max_exposure (default: 10%).
Verifies stop-loss ratio ≥ min_sl_ratio (default: 1%).


Strategy Validation (strategy_filter.rs, goal_alignment.rs):
Validates strategy completeness (entry/exit prices).
Checks for overfitting and timestamp validity (<300s).
Ensures risk-reward ratio ≤ max_risk_reward_ratio (default: 2.0).


Market Conditions Validation (liquidity_validator.rs, time_sensitivity.rs):
Confirms size/market_depth ≤ min_liquidity_ratio (default: 5%).
Ensures time drift ≤ max_time_drift (default: 30s).


Compliance, Cost, Consistency (compliance.rs, cost_analysis.rs, consistency.rs):
Verifies region compliance and restricted symbols.
Checks slippage ≤ max_slippage_bps (default: 50bps) and commission ≤ max_commission_pct (default: 0.1%).
Detects conflicting positions or excessive signals.


Verdict Output (orchestrator.rs):
Outputs JSON verdict: "valid," "warning," or "reject" with details.
Publishes to validation_output Redis channel.
Logs errors to validation:errors.



Failure Handling

Any stage failure results in a "reject" verdict with specific reasons.
Valid inputs are forwarded to the Execution Agent via mpsc channel.
Learning layer (research_engine.py) analyzes failures for rule refinement.
