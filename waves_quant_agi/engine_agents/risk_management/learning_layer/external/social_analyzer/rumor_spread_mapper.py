from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ....logs.risk_management_logger import RiskManagementLogger

class RumorSpreadMapper:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.rumor_impact_threshold = config.get("rumor_impact_threshold", 0.6)  # 60% impact confidence

    async def detect_rumors(self, social_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect rumor-driven volatility for risk signals."""
        try:
            rumor_results = []
            for _, row in social_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                rumor_impact_score = float(row.get("rumor_impact_score", 0.0))

                if rumor_impact_score >= self.rumor_impact_threshold:
                    result = {
                        "type": "rumor_detection",
                        "symbol": symbol,
                        "rumor_impact_score": rumor_impact_score,
                        "timestamp": int(time.time()),
                        "description": f"Rumor-driven volatility detected for {symbol}: Impact {rumor_impact_score:.2f}"
                    }
                    rumor_results.append(result)
                    self.logger.log_risk_assessment("assessment", result)
                    self.redis_client.set(f"risk_management:rumor_detection:{symbol}", str(result), ex=3600)
                    await self.notify_execution(result)
                else:
                    result = {
                        "type": "rumor_detection",
                        "symbol": symbol,
                        "rumor_impact_score": rumor_impact_score,
                        "timestamp": int(time.time()),
                        "description": f"No significant rumor impact for {symbol}: Impact {rumor_impact_score:.2f}"
                    }
                    rumor_results.append(result)
                    self.logger.log_risk_assessment("assessment", result)

            summary = {
                "type": "rumor_detection_summary",
                "result_count": len(rumor_results),
                "timestamp": int(time.time()),
                "description": f"Analyzed {len(rumor_results)} rumor-driven volatility signals"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return rumor_results
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_execution(self, result: Dict[str, Any]):
        """Notify Executions Agent of significant rumor signals."""
        self.logger.log(f"Notifying Executions Agent: {result.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(result))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of rumor detection results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))