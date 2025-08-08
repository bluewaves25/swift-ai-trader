from typing import Dict, Any, List
import networkx as nx
import time
from ..logs.intelligence_logger import IntelligenceLogger
from .agent_graph_builder import AgentGraphBuilder

class FeedbackLoopMonitor:
    def __init__(self, config: Dict[str, Any], logger: IntelligenceLogger, graph_builder: AgentGraphBuilder):
        self.config = config
        self.logger = logger
        self.graph_builder = graph_builder
        self.feedback_threshold = config.get("feedback_threshold", 0.8)

    async def monitor_feedback_loops(self, agent_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect and monitor feedback loops in agent interactions."""
        try:
            graph_data = await self.graph_builder.build_agent_graph(agent_metrics)
            if not graph_data:
                self.logger.log_info("Empty graph data for feedback monitoring")
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
                        self.logger.log_alert(loop)

            result = {
                "type": "feedback_monitoring",
                "loop_count": len(loops),
                "timestamp": int(time.time()),
                "description": f"Detected {len(loops)} feedback loops"
            }
            self.logger.log_alert(result)
            await self.notify_core(result)
            return loops
        except Exception as e:
            self.logger.log_error(f"Error monitoring feedback loops: {e}")
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of feedback loop detections."""
        self.logger.log_info(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish to Core Agent