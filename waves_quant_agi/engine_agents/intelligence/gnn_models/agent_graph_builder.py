from typing import Dict, Any, List
import networkx as nx
import time
from ..logs.intelligence_logger import IntelligenceLogger

class AgentGraphBuilder:
    def __init__(self, config: Dict[str, Any], logger: IntelligenceLogger):
        self.config = config
        self.logger = logger
        self.dependency_threshold = config.get("dependency_threshold", 0.5)

    async def build_agent_graph(self, agent_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a graph of agent relationships based on metrics and interactions."""
        try:
            graph = nx.DiGraph()
            for metric in agent_metrics:
                agent = metric.get("agent", "unknown")
                graph.add_node(agent, **{k: v for k, v in metric.items() if k != "agent"})

            # Add edges based on metric correlations or shared tasks
            for i, m1 in enumerate(agent_metrics):
                for m2 in agent_metrics[i+1:]:
                    agent1, agent2 = m1.get("agent"), m2.get("agent")
                    if agent1 and agent2:
                        # Placeholder: Calculate dependency score (e.g., shared task overlap)
                        dependency_score = self._calculate_dependency(m1, m2)
                        if dependency_score > self.dependency_threshold:
                            graph.add_edge(agent1, agent2, weight=dependency_score)
                            graph.add_edge(agent2, agent1, weight=dependency_score)

            result = {
                "type": "agent_graph",
                "nodes": list(graph.nodes),
                "edges": list(graph.edges(data=True)),
                "timestamp": int(time.time()),
                "description": f"Built agent graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges"
            }
            self.logger.log_alert(result)
            await self.notify_core(result)
            return {"graph": graph, "metadata": result}
        except Exception as e:
            self.logger.log_error(f"Error building agent graph: {e}")
            return {}

    def _calculate_dependency(self, m1: Dict[str, Any], m2: Dict[str, Any]) -> float:
        """Calculate dependency score between two agents (placeholder)."""
        # Mock: Based on shared task overlap or metric similarity
        return 0.6 if m1.get("task_type") == m2.get("task_type") else 0.3

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of graph construction."""
        self.logger.log_info(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish to Core Agent