from typing import Dict, Any, List
import time
import pandas as pd
import numpy as np

class UncertaintyEntropyModel:
    def __init__(self, connection_manager, config: Dict[str, Any]):
        self.config = config
        self.connection_manager = connection_manager
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
                # Store measure in Redis using connection manager
                redis_client = await self.connection_manager.get_redis_client()
                if redis_client:
                    redis_client.set(f"risk_management:entropy:{symbol}", str(measure), ex=3600)
                    if measure["description"].startswith("High entropy"):
                        await self.notify_execution(measure)

            summary = {
                "type": "entropy_measure_summary",
                "measure_count": len(entropy_measures),
                "timestamp": int(time.time()),
                "description": f"Measured entropy for {len(entropy_measures)} symbols"
            }
            await self.notify_core(summary)
            return entropy_measures
        except Exception as e:
            print(f"Error in uncertainty entropy model: {e}")
            return []

    async def notify_execution(self, measure: Dict[str, Any]):
        """Notify Executions Agent of high entropy risks."""
        print(f"Notifying Executions Agent: {measure.get('description', 'unknown')}")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("execution_agent", str(measure))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of entropy measurement results."""
        print(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("risk_management_output", str(issue))