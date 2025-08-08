from typing import Dict, Any, List
import time
import redis
import pandas as pd
import numpy as np
from ..logs.risk_management_logger import RiskManagementLogger

class UncertaintyEntropyModel:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.entropy_threshold = config.get("entropy_threshold", 0.8)  # 80% entropy threshold

    async def measure_entropy(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Measure entropy for risk of unknown."""
        try:
            entropy_measures = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                price_changes = row.get("price_changes", np.array([]))
                if len(price_changes) > 0:
                    probabilities = np.histogram(price_changes, bins=10, density=True)[0]
                    entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
                else:
                    entropy = 0.0

                if entropy > self.entropy_threshold:
                    measure = {
                        "type": "entropy_measure",
                        "symbol": symbol,
                        "entropy": entropy,
                        "timestamp": int(time.time()),
                        "description": f"High entropy detected for {symbol}: Entropy {entropy:.2f}"
                    }
                else:
                    measure = {
                        "type": "entropy_measure",
                        "symbol": symbol,
                        "entropy": entropy,
                        "timestamp": int(time.time()),
                        "description": f"Acceptable entropy for {symbol}: Entropy {entropy:.2f}"
                    }

                entropy_measures.append(measure)
                self.logger.log_risk_assessment("assessment", measure)
                self.redis_client.set(f"risk_management:entropy:{symbol}", str(measure), ex=3600)
                if measure["description"].startswith("High entropy"):
                    await self.notify_execution(measure)

            summary = {
                "type": "entropy_measure_summary",
                "measure_count": len(entropy_measures),
                "timestamp": int(time.time()),
                "description": f"Measured entropy for {len(entropy_measures)} symbols"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return entropy_measures
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_execution(self, measure: Dict[str, Any]):
        """Notify Executions Agent of high entropy risks."""
        self.logger.log(f"Notifying Executions Agent: {measure.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(measure))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of entropy measurement results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))