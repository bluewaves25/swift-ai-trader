from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ....logs.risk_management_logger import RiskManagementLogger

class MarketRegimeClassifier:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.regime_confidence_threshold = config.get("regime_confidence_threshold", 0.7)  # 70% confidence

    async def classify_regime(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Predict market regime shifts."""
        try:
            regime_results = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                regime_confidence = float(row.get("regime_confidence", 0.0))
                regime_type = row.get("regime_type", "unknown")

                if regime_confidence >= self.regime_confidence_threshold:
                    result = {
                        "type": "market_regime",
                        "symbol": symbol,
                        "regime_type": regime_type,
                        "regime_confidence": regime_confidence,
                        "timestamp": int(time.time()),
                        "description": f"Market regime shift detected for {symbol}: {regime_type} (Confidence {regime_confidence:.2f})"
                    }
                    regime_results.append(result)
                    self.logger.log_risk_assessment("assessment", result)
                    self.redis_client.set(f"risk_management:market_regime:{symbol}", str(result), ex=3600)
                    await self.notify_execution(result)
                else:
                    result = {
                        "type": "market_regime",
                        "symbol": symbol,
                        "regime_type": regime_type,
                        "regime_confidence": regime_confidence,
                        "timestamp": int(time.time()),
                        "description": f"No significant regime shift for {symbol}: {regime_type} (Confidence {regime_confidence:.2f})"
                    }
                    regime_results.append(result)
                    self.logger.log_risk_assessment("assessment", result)

            summary = {
                "type": "market_regime_summary",
                "result_count": len(regime_results),
                "timestamp": int(time.time()),
                "description": f"Classified {len(regime_results)} market regimes"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return regime_results
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_execution(self, result: Dict[str, Any]):
        """Notify Executions Agent of detected regime shifts."""
        self.logger.log(f"Notifying Executions Agent: {result.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(result))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of market regime classification results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))