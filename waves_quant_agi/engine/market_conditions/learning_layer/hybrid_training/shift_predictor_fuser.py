from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class ShiftPredictorFuser:
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
        self.fusion_threshold = config.get("fusion_threshold", 0.7)  # Confidence threshold for fused predictions

    async def fuse_shift_predictions(self, predictions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fuse multiple shift predictions into a single signal."""
        try:
            fused_signals = []
            for data in predictions:
                symbol = data.get("symbol", "unknown")
                prediction_scores = data.get("prediction_scores", [])
                sources = data.get("sources", [])

                fused_score = self._calculate_fused_score(prediction_scores)
                if fused_score > self.fusion_threshold:
                    signal = {
                        "type": "fused_shift_signal",
                        "symbol": symbol,
                        "sources": sources,
                        "fused_score": fused_score,
                        "timestamp": int(time.time()),
                        "description": f"Fused shift signal for {symbol} from {len(sources)} sources: score {fused_score:.2f}"
                    }
                    fused_signals.append(signal)
                    self.logger.log_issue(signal)
                    self.cache.store_incident(signal)
                    self.redis_client.set(f"market_conditions:fused_shift:{symbol}", str(signal), ex=604800)  # Expire after 7 days

            summary = {
                "type": "fused_shift_summary",
                "signal_count": len(fused_signals),
                "timestamp": int(time.time()),
                "description": f"Fused {len(fused_signals)} shift predictions"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return fused_signals
        except Exception as e:
            self.logger.log(f"Error fusing shift predictions: {e}")
            self.cache.store_incident({
                "type": "shift_predictor_fuser_error",
                "timestamp": int(time.time()),
                "description": f"Error fusing shift predictions: {str(e)}"
            })
            return []

    def _calculate_fused_score(self, prediction_scores: List[float]) -> float:
        """Calculate fused prediction score (placeholder)."""
        # Mock: Weighted average of scores
        return sum(prediction_scores) / len(prediction_scores) if prediction_scores else 0.0

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of fused shift prediction results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))