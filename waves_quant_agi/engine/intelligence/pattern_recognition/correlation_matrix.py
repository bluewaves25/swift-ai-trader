from typing import Dict, Any, List
import pandas as pd
import redis
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache

class CorrelationMatrix:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.correlation_threshold = config.get("correlation_threshold", 0.7)

    async def build_correlation_matrix(self, agent_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build correlation matrix for agent performance metrics."""
        try:
            if not agent_metrics:
                self.logger.log("Empty agent metrics for correlation analysis")
                return {}

            # Prepare DataFrame from agent metrics
            metrics_df = pd.DataFrame([
                {
                    "agent": m.get("agent", "unknown"),
                    "speed": float(m.get("speed", 0.0)),
                    "accuracy": float(m.get("accuracy", 0.0)),
                    "cost": float(m.get("cost", 0.0)),
                    "error_rate": float(m.get("error_rate", 0.0))
                } for m in agent_metrics
            ])

            # Compute correlation matrix
            corr_matrix = metrics_df.drop(columns=["agent"]).corr().to_dict()
            high_correlations = {
                (col1, col2): value
                for col1, cols in corr_matrix.items()
                for col2, value in cols.items()
                if abs(value) > self.correlation_threshold and col1 != col2
            }

            result = {
                "type": "correlation_matrix",
                "correlations": high_correlations,
                "timestamp": int(time.time()),
                "description": f"Found {len(high_correlations)} significant correlations"
            }
            self.logger.log_issue(result)
            self.cache.store_incident(result)
            self.redis_client.set("intelligence:correlation_matrix", str(high_correlations), ex=604800)  # Expire after 7 days
            await self.notify_core(result)
            return result
        except Exception as e:
            self.logger.log(f"Error building correlation matrix: {e}")
            self.cache.store_incident({
                "type": "correlation_matrix_error",
                "timestamp": int(time.time()),
                "description": f"Error building correlation matrix: {str(e)}"
            })
            return {}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of correlation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish to Core Agent