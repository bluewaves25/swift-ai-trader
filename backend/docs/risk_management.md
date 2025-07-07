Risk Management
Philosophy
"Loss-Driven Evolution": Losses trigger upgrades.
PLPB

Micro-audit (500ms): Market, strategy, execution (Redis).
Categorization: Adjust volatility (VIX), penalize strategies, retry executions.
AI: PPO/DQN, online learning, anomaly detection.

Capital Flow

Small Loss (≤0.5%): Log with SHAP.
Medium Loss (0.5–1.5%): Reduce lot size 30%.
Large Loss (>1.5%): Suspend strategy, retrain.

Cooldown Mode

≥97% confidence, 4:1 reward/risk.
Recover after 4 wins or 3% gain.
