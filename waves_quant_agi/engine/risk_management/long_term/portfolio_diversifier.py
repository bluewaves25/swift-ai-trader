from typing import Dict, Any, List
import redis
import pandas as pd
import numpy as np
from ..market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ..market_conditions.memory.incident_cache import IncidentCache

class PortfolioDiversifier:
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
        self.correlation_threshold = config.get("correlation_threshold", 0.3)  # Max correlation for diversification

    async def assess_diversification(self, portfolio_data: pd.DataFrame) -> float:
        """Assess portfolio diversification across uncorrelated assets."""
        try:
            symbols = portfolio_data.get("symbol", []).unique()
            if len(symbols) < 2:
                self.logger.log("Insufficient assets for diversification")
                return 0.0

            # Calculate correlation matrix (placeholder)
            returns = portfolio_data.pivot(columns="symbol", values="returns").fillna(0)
            correlation_matrix = np.corrcoef(returns.values.T)
            max_correlation = np.max(np.abs(correlation_matrix - np.eye(len(symbols))))

            diversification_score = 1.0 - max_correlation
            if max_correlation > self.correlation_threshold:
                issue = {
                    "type": "diversification_issue",
                    "symbols": list(symbols),
                    "max_correlation": float(max_correlation),
                    "timestamp": int(time.time()),
                    "description": f"High correlation detected: {max_correlation:.2f}"
                }
                self.logger.log_issue(issue)
                self.cache.store_incident(issue)
                self.redis_client.set("risk_management:diversification", str(issue), ex=604800)

            summary = {
                "type": "diversification_summary",
                "score": diversification_score,
                "timestamp": int(time.time()),
                "description": f"Portfolio diversification score: {diversification_score:.2f}"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return diversification_score
        except Exception as e:
            self.logger.log(f"Error assessing diversification: {e}")
            self.cache.store_incident({
                "type": "portfolio_diversifier_error",
                "timestamp": int(time.time()),
                "description": f"Error assessing diversification: {str(e)}"
            })
            return 0.0

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of diversification results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))