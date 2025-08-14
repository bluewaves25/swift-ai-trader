# Core Agent Overview - SYSTEM COORDINATION ONLY

## Mission
The Core Agent serves as the **SINGLE SOURCE OF TRUTH FOR SYSTEM COORDINATION**, managing system health monitoring, timing coordination, and agent coordination flows. It does NOT handle trading, strategy execution, or market operations - these are now consolidated in the Strategy Engine Agent.

## Behavior

- **System Health Monitoring**: Coordinates health checks across all agents using SystemSignalFilter
- **Timing Coordination**: Manages 4-tier timing architecture (Ultra-HFT, Fast, Tactical, Strategic) via SystemCoordinationFlowManager
- **Agent Coordination**: Orchestrates system-wide coordination flows using SystemCoordinationLogicExecutor
- **System Command Routing**: Builds and routes system coordination commands via SystemCoordinationPipeline
- **Context Management**: Stores health checks, timing syncs, and coordination events in SystemCoordinationContext
- **Coordination Learning**: Feeds coordination data to SystemCoordinationResearchEngine for system optimization
- **Logging**: Records all coordination actions and errors using CoreAgentLogger

## Dependencies

### External Libraries:
- `asyncio`: For asynchronous coordination loops
- `logging`: For persistent logging with rotation
- `redis`: For inter-agent communication
- `time`: For timing coordination and health monitoring

### Internal Modules:
- `controller/`: System coordination logic execution, signal filtering, and flow management
- `interfaces/`: System coordination communication interface
- `pipeline/`: Coordination request packaging and routing
- `memory/`: Context storage for health checks, timing syncs, and coordination events
- `learning_layer/`: System coordination research, training, and retraining logic
- `logs/`: Logging infrastructure

## Scalability

- Modular design supports adding new coordination types via SystemCoordinationIO
- SystemCoordinationContext uses fixed-size deques for memory efficiency
- SystemCoordinationRetrainingLoop runs periodically to adapt to new coordination patterns
- Logging uses rotating files to manage disk space
- Redis-based communication scales horizontally across multiple agent instances

## Key Differences from Previous Version

- **REMOVED**: All trading signal processing, trade command creation, and execution routing
- **REMOVED**: Strategy approval, risk compliance checking, and market data handling
- **REMOVED**: PnL tracking, trade rejection handling, and market context management
- **ADDED**: System health monitoring, timing coordination, and agent status management
- **ADDED**: Coordination flow management and system command routing
- **ADDED**: System coordination learning and pattern analysis

## Integration Points

- **Strategy Engine Agent**: Receives system coordination commands and health status updates
- **All Other Agents**: Send health checks, timing syncs, and status updates to Core Agent
- **Redis**: Central communication hub for all system coordination messages
- **System Clock**: Master timing reference for 4-tier architecture coordination
