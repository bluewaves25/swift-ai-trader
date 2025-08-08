Core Agent Overview
Mission
The Core Agent serves as the centralized logic and flow control layer, validating and routing trade commands, coordinating agents (Strategy, Risk, Adapter), managing context, and integrating learning without executing trades. It enforces a strict logic tree, ensures traceability, and adapts dynamically based on market context.
Behavior

Signal Validation: Filters signals using SignalFilter based on predefined rules.
Logic Execution: Processes signals through LogicExecutor using conditional logic trees.
Agent Coordination: Orchestrates agent interactions via FlowManager (Strategy → Risk → Adapter).
Command Routing: Builds and sends trade commands to execution via ExecutionPipeline.
Context Management: Stores signals, rejections, and PnL snapshots in RecentContext.
Learning Integration: Feeds data to ResearchEngine, TrainingModule, and RetrainingLoop for optimization.
Logging: Records all actions and errors using CoreAgentLogger.

Dependencies

External Libraries:
asyncio: For asynchronous retraining loops.
logging: For persistent logging with rotation.
dataclasses: For structured TradeCommand objects.
collections.deque: For efficient context storage.


Internal Modules:
controller/: Logic execution, signal filtering, and flow management.
interfaces/: Trade command model and agent communication.
pipeline/: Command packaging and routing.
memory/: Context storage for signals and rejections.
learning_layer/: Research, training, and retraining logic.
logs/: Logging infrastructure.



Scalability

Modular design supports adding new strategies or agents via AgentIO.
RecentContext uses fixed-size deques for memory efficiency.
RetrainingLoop runs periodically to adapt to new data.
Logging uses rotating files to manage disk space.
