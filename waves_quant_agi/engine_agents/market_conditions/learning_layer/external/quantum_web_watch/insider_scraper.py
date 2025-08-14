import time
from typing import Dict, Any, List
import redis
from ....logs.failure_agent_logger import FailureAgentLogger
from ....logs.incident_cache import IncidentCache

class InsiderScraper:
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
        self.signal_threshold = config.get("signal_threshold", 0.5)  # Confidence threshold for signals

    async def scrape_insider_signals(self, external_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse SEC filings, LinkedIn job moves, etc. for insider signals."""
        try:
            signals = []
            for data in external_data:
                symbol = data.get("symbol", "unknown")
                signal_score = float(data.get("signal_score", 0.0))
                source = data.get("source", "unknown")

                if signal_score > self.signal_threshold:
                    signal = {
                        "type": "insider_signal",
                        "symbol": symbol,
                        "source": source,
                        "signal_score": signal_score,
                        "timestamp": int(time.time()),
                        "description": f"Insider signal for {symbol} from {source}: score {signal_score:.2f}"
                    }
                    signals.append(signal)
                    self.logger.log_issue(signal)
                    self.cache.store_incident(signal)
                    self.redis_client.set(f"market_conditions:insider_scrape:{symbol}", str(signal), ex=604800)  # Expire after 7 days

            summary = {
                "type": "insider_scrape_summary",
                "signal_count": len(signals),
                "timestamp": int(time.time()),
                "description": f"Scraped {len(signals)} insider signals"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return signals
        except Exception as e:
            self.logger.log(f"Error scraping insider signals: {e}")
            self.cache.store_incident({
                "type": "insider_scraper_error",
                "timestamp": int(time.time()),
                "description": f"Error scraping insider signals: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of insider signal results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))