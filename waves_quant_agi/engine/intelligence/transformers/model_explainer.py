from typing import Dict, Any, List
import redis
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache
from .inter_agent_transformer import InterAgentTransformer

class ModelExplainer:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache, transformer: InterAgentTransformer):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.transformer = transformer
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.explanation_key = config.get("explanation_key", "intelligence:explanations")

    async def explain_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanations for agent coordination decisions."""
        try:
            interaction = {
                "agent1": decision.get("agent1", "unknown"),
                "agent2": decision.get("agent2", "unknown"),
                "task": decision.get("task", "unknown")
            }
            embedding_data = await self.transformer.process_interactions([interaction])
            embedding = embedding_data.get("embeddings", [[]])[0]

            # Placeholder: Generate explanation based on embedding
            explanation_text = self._generate_explanation(decision, embedding)
            explanation = {
                "type": "decision_explanation",
                "agents": [interaction["agent1"], interaction["agent2"]],
                "task": interaction["task"],
                "explanation": explanation_text,
                "timestamp": int(time.time()),
                "description": f"Explained decision for {interaction['task']} between {interaction['agent1']} and {interaction['agent2']}"
            }
            self.logger.log_issue(explanation)
            self.cache.store_incident(explanation)
            self.redis_client.set(self.explanation_key, str(explanation), ex=604800)  # Expire after 7 days
            await self.notify_core(explanation)
            return explanation
        except Exception as e:
            self.logger.log(f"Error explaining decision: {e}")
            self.cache.store_incident({
                "type": "model_explainer_error",
                "timestamp": int(time.time()),
                "description": f"Error explaining decision: {str(e)}"
            })
            return {}

    def _generate_explanation(self, decision: Dict[str, Any], embedding: List[float]) -> str:
        """Generate explanation text (placeholder)."""
        # Mock: Simple explanation based on decision and embedding norm
        norm = sum(x**2 for x in embedding) ** 0.5 if embedding else 0.0
        return f"Decision to prioritize {decision.get('resolution', 'unknown')} due to high interaction strength ({norm:.4f})"

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of decision explanations."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish to Core Agent