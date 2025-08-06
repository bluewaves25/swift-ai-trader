from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class SupplySourceTracer:
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
        self.source_threshold = config.get("source_threshold", 0.5)  # Confidence score for source

    async def trace_supply_source(self, shocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Trace origin of sudden supply surges."""
        try:
            sources = []
            for shock in shocks:
                symbol = shock.get("symbol", "unknown")
                shock_type = shock.get("shock_type", "unknown")
                # Placeholder: Analyze order book or external data for source
                source = self._analyze_source(shock)
                source_info = {
                    "type": "supply_source",
                    "symbol": symbol,
                    "shock_type": shock_type,
                    "source": source["source"],
                    "confidence": source["confidence"],
                    "timestamp": int(time.time()),
                    "description": f"Supply {shock_type} for {symbol} traced to {source['source']} (confidence: {source['confidence']:.2f})"
                }
                sources.append(source_info)
                self.logger.log_issue(source_info)
                self.cache.store_incident(source_info)
                self.redis_client.set(f"market_conditions:source:{symbol}", str(source_info), ex=604800)  # Expire after 7 days

            summary = {
                "type": "supply_source_summary",
                "source_count": len(sources),
                "timestamp": int(time.time()),
                "description": f"Traced {len(sources)} supply sources"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return sources
        except Exception as e:
            self.logger.log(f"Error tracing supply sources: {e}")
            self.cache.store_incident({
                "type": "supply_source_error",
                "timestamp": int(time.time()),
                "description": f"Error tracing supply sources: {str(e)}"
            })
            return []

    def _analyze_source(self, shock: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze source of supply shock (placeholder)."""
        # Mock: Determine internal/external source
        return {"source": "external_exchange" if shock.get("volume", 0) > 1000 else "internal_order", "confidence": 0.6}

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of supply source results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))