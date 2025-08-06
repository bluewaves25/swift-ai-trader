Integration Guide: Adding a New Agent
Steps to Add a New Agent

Define Agent Interface:

Update AgentIO in core/interfaces/agent_io.py to include communication methods for the new agent.
Example:def send_to_new_agent(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # Implement communication logic
    pass




Update Flow Manager:

Modify FlowManager in core/controller/flow_manager.py to coordinate with the new agent.
Example:def coordinate_agents(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # Add new agent coordination
    new_response = self.agent_io.send_to_new_agent(signal)
    if new_response and new_response.get("approved"):
        return new_response
    return None




Register in Logic Executor:

Ensure LogicExecutor in core/controller/logic_executor.py includes the new agent in its logic tree if needed.
Example:if new_response := self.flow_manager.coordinate_agents(signal):
    trade_command = TradeCommand(...)




Update Signal Filter:

Add new strategy validation in SignalFilter if the agent introduces new signal types.
Example:self.valid_strategies.add("new_strategy")




Context and Logging:

Ensure RecentContext in core/memory/recent_context.py can store relevant data from the new agent.
Verify CoreAgentLogger in core/logs/core_agent_logger.py logs new agent actions.
Example log:self.logger.log_action("new_agent_action", {"data": data})




Training Integration:

Update ResearchEngine and TrainingModule in core/learning_layer/ to include new agent data in datasets.
Example:dataset_entry["new_agent_data"] = new_response




Test Integration:

Simulate signals and validate flow through LogicExecutor and ExecutionPipeline.
Check logs in logs/*.log for new agent actions and errors.
Test retraining with RetrainingLoop to ensure new data is processed.



Best Practices

Use AgentIO for all external agent communication to maintain modularity.
Log every action and error using CoreAgentLogger for traceability.
Validate new signal types in SignalFilter to ensure compatibility.
Test with simulated data before deploying to production.
Update api_documentation.md with new agent API details.
