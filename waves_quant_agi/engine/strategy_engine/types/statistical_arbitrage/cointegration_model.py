from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class CointegrationModel:
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
        self.coint_threshold = config.get("coint_threshold", 0.05)  # Cointegration p-value

    async def detect_coint_opportunity(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect cointegration-based trading opportunities."""
        try:
            opportunities = []
            for _, row in market_data.iterrows():
                symbol1 = row.get("symbol1", "EUR/USD")
                symbol2 = row.get("symbol2", "GBP/USD")
                coint_pvalue = float(row.get("coint_pvalue", 1.0))
                spread = float(row.get("spread", 0.0))

                if coint_pvalue < self.coint_threshold and abs(spread) > self.config.get("spread_threshold", 0.01):
                    signal = "buy" if spread > 0 else "sell"
                    pair = f"{symbol1}/{symbol2}"
                    opportunity = {
                        "type": "cointegration_model",
                        "pair": pair,
                        "signal": signal,
                        "coint_pvalue": coint_pvalue,
                        "spread": spread,
                        "timestamp": int(time.time()),
                        "description": f"Cointegration for {pair}: P-value {coint_pvalue:.4f}, Spread {spread:.4f}"
                    }
                    opportunities.append(opportunity)
                    self.logger.log_issue(opportunity)
                    self.cache.store_incident(opportunity)
                    self.redis_client.set(f"strategy_engine:cointegration:{pair}", str(opportunity), ex=3600)
                    await self.notify_execution(opportunity)

            summary = {
                "type": "cointegration_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} cointegration opportunities"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error detecting cointegration: {e}")
            self.cache.store_incident({
                "type": "cointegration_model_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting cointegration: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of cointegration signal."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of cointegration results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))