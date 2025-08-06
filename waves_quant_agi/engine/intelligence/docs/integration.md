Integration Guide
Purpose
Integrate the Intelligence Agent with Core and other agents (e.g., Fees Monitor, Strategy) to optimize system-level coordination and performance.
Integration Steps

Redis Configuration:

Subscribe Core Agent to Redis channel "intelligence_instruction".
Example:from intelligence.memory.incident_cache import IncidentCache
cache = IncidentCache(logger)
instructions = cache.retrieve_incidents("intelligence:*")




Input Schema:

Agent metrics from Core Agent:{
  "agent": str,
  "speed": float,
  "accuracy": float,
  "cost": float,
  "error_rate": float,
  "task": str,
  "performance_score": float
}


Interaction/conflict data:{
  "agent1": str,
  "agent2": str,
  "task": str,
  "resolution": str  # Optional
}


Social data:{
  "agent": str,
  "text": str,
  "source": str
}




Adding New Agents:

Update config with new agent metrics and tasks.
Example:config["new_agent"] = {"metrics": ["speed", "accuracy"], "tasks": ["trade_execution"]}




External Data Integration:

Configure ai_lab_urls, case_urls, architecture_urls in AILabScraper, OrchestrationCases, ArchitectureMonitor.
Feed social data to AgentSentiment, SystemConfidence.
Example:from intelligence.learning_layer.external.social_analyzer.agent_sentiment import AgentSentiment
sentiment = AgentSentiment(config, logger, cache)
await sentiment.analyze_sentiment([{"agent": "FeesMonitor", "text": "high fees", "source": "X"}])




Testing:

Simulate metrics with varied performance (e.g., high error rates).
Verify Redis caching (IncidentCache.retrieve_incidents).
Test conflict resolution with mock conflicts.
Example:conflicts = [{"agent1": "FeesMonitor", "agent2": "Strategy", "task": "trade_execution"}]
resolver = ConflictResolver(config, logger, cache, transformer)
await resolver.resolve_conflicts(conflicts)





Best Practices

Use consistent Redis channel names (e.g., "intelligence_instruction").
Validate input schemas before processing.
Monitor scraping latency for external data sources.
Log all actions via FailureAgentLogger to Redis.
Test with scenarios like agent conflicts or low system confidence.

Dependencies

Libraries: pandas, networkx, torch, torch_geometric, transformers, vaderSentiment, requests, BeautifulSoup.
Shared: IncidentCache, FailureAgentLogger for caching/logging.
