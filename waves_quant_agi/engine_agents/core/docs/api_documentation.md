API Documentation
Internal API Specifications
Trade Command Format
The TradeCommand object, defined in trade_model.py, standardizes trade commands:

Fields:
signal_id: String, unique signal identifier.
strategy: String, trading strategy (e.g., "momentum", "mean_reversion").
params: Dict, order details (e.g., {"amount": 0.1, "base": "BTC", "quote": "USDT"}).
metadata: Dict, additional data (e.g., {"timestamp": 1234567890.0}).



Key Components

LogicExecutor:
execute_logic_tree(signal): Processes signal through logic tree, returns TradeCommand or None.


FlowManager:
check_risk_compliance(signal): Returns {"passed": bool, "reason": str} for risk checks.
route_to_execution(trade_command): Sends command to execution agent, returns bool.
coordinate_agents(signal): Coordinates with strategy/risk agents, returns response or None.


SignalFilter:
validate_signal(signal): Validates signal format and strategy, returns bool.


AgentIO:
send_to_strategy(signal): Sends signal to strategy agent, returns response or None.
send_to_risk(signal): Sends signal to risk agent, returns response or None.
send_to_execution(trade_command): Sends command to execution agent, returns bool.


ExecutionPipeline:
build_command_package(trade_command): Builds command package, returns dict or None.
send_to_execution(trade_command): Sends package to execution agent, returns bool.


RecentContext:
store_signal(signal): Stores signal in context.
store_rejection(signal_id, reason): Stores rejection details.
store_pnl_snapshot(snapshot): Stores PnL snapshot.
get_recent_signals(): Returns list of recent signals.
get_recent_rejections(): Returns list of recent rejections.
get_recent_pnl(): Returns list of recent PnL snapshots.


ResearchEngine:
analyze_behavior(): Returns analysis of agent behavior.
collect_market_data(external_data): Returns processed market data.


TrainingModule:
prepare_dataset(): Returns list of dataset entries for training.
train_model(dataset): Trains model, returns metrics.


RetrainingLoop:
run_retraining(): Runs periodic retraining loop.



External Agent API Specifications
Strategy Agent

Input: Signal dict ({"signal_id": str, "strategy": str, "params": dict, "timestamp": float}).
Output: {"approved": bool, "signal_id": str, "reason": str (optional)}.
Interaction: Via AgentIO.send_to_strategy(signal).

Risk Agent

Input: Signal dict (same as above).
Output: {"passed": bool, "signal_id": str, "reason": str (optional)}.
Interaction: Via AgentIO.send_to_risk(signal).

Execution Agent (Adapters Agent)

Input: Command package ({"command": TradeCommand.to_dict(), "timestamp": float, "priority": float}).
Output: Bool (success/failure).
Interaction: Via AgentIO.send_to_execution(trade_command).

Notes

All components use CoreAgentLogger for action and error logging in logs/*.log.
RecentContext uses fixed-size deques for efficient storage.
RetrainingLoop runs asynchronously to update models periodically.
Extend AgentIO for new agents and update this file with their API details.
