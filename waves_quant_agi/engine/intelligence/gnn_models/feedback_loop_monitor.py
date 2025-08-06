from typing import Dict, Any, List
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache
from .agent_graph_builder import AgentGraphBuilder

class FeedbackLoopMonitor:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache, graph_builder: AgentGraphBuilder):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.graph_builder = graph_builder
        self.feedback_threshold = config.get("feedback_threshold", 0.8)

    async def monitor_feedback_loops(self, agent_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect and monitor feedback loops in agent interactions."""
        try:
            graph_data = await self.graph_builder.build_agent_graph(agent_metrics)
            if not graph_data:
                self.logger.log("Empty graph data for feedback monitoring")
                return []

            graph = graph_data["graph"]
            loops = []
            for cycle in nx.simple_cycles(graph):
                if len(cycle) > 1:  # Ignore self-loops
                    loop_weight = sum(graph[u][v]["weight"] for u, v in zip(cycle, cycle[1:] + cycle[:1]))
                    if loop_weight > self.feedback_threshold:
                        loop = {
                            "type": "feedback_loop",
                            "agents": cycle,
                            "weight": loop_weight,
                            "timestamp": int(time.time()),
                            "description": f"Feedback loop detected among {cycle} with weight {loop_weight:.4f}"
                        }
                        loops.append(loop)
                        self.logger.log_issue(loop)
                        self.cache.store_incident(loop)

            result = {
                "type": "feedback_monitoring",
                "loop_count": len(loops),
                "timestamp": int(time.time()),
                "description": f"Detected {len(loops)} feedback loops"
            }
            self.logger.log_issue(result)
            self.cache.store_incident(result)
            await self.notify_core(result)
            return loops
        except Exception as e:
            self.logger.log(f"Error monitoring feedback loops: {e}")
            self.cache.store_incident({
                "type": "feedback_monitor_error",
                "timestamp": int(time.time()),
                "description": f"Error monitoring feedback loops: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of feedback loop detections."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish to Core Agent