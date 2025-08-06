from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class EconomicSignalAggregator:
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
        self.signal_weight = config.get("signal_weight", 0.5)  # Minimum signal weight

    async def aggregate_economic_signals(self, macro_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregate macro-economic signals for market impact."""
        try:
            signals = []
            for data in macro_data:
                symbol = data.get("symbol", "unknown")
                signal_strength = float(data.get("signal_strength", 0.0))
                source = data.get("source", "unknown")

                if signal_strength > self.signal_weight:
                    signal = {
                        "type": "economic_signal",
                        "symbol": symbol,
                        "source": source,
                        "signal_strength": signal_strength,
                        "timestamp": int(time.time()),
                        "description": f"Economic signal for {symbol} from {source}: strength {signal_strength:.2f}"
                    }
                    signals.append(signal)
                    self.logger.log_issue(signal)
                    self.cache.store_incident(signal)
                    self.redis_client.set(f"market_conditions:economic:{symbol}", str(signal), ex=604800)  # Expire after 7 days

            summary = {
                "type": "economic_signal_summary",
                "signal_count": len(signals),
                "timestamp": int(time.time()),
                "description": f"Aggregated {len(signals)} economic signals"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return signals
        except Exception as e:
            self.logger.log(f"Error aggregating economic signals: {e}")
            self.cache.store_incident({
                "type": "economic_signal_error",
                "timestamp": int(time.time()),
                "description": f"Error aggregating economic signals: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of economic signal results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))