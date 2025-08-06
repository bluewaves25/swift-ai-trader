from typing import Dict, Any, List
import redis
from .....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from .....market_conditions.memory.incident_cache import IncidentCache

class AILabScraper:
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
        self.relevance_threshold = config.get("relevance_threshold", 0.6)  # Research relevance score

    async def scrape_research(self, research_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Scrape AI research for strategy enhancement."""
        try:
            insights = []
            for data in research_data:
                source = data.get("source", "unknown")
                relevance_score = float(data.get("relevance_score", 0.0))
                strategy_id = data.get("strategy_id", "unknown")

                if relevance_score > self.relevance_threshold:
                    insight = {
                        "type": "research_insight",
                        "strategy_id": strategy_id,
                        "source": source,
                        "relevance_score": relevance_score,
                        "timestamp": int(time.time()),
                        "description": f"Research insight for {strategy_id} from {source}: Score {relevance_score:.2f}"
                    }
                    insights.append(insight)
                    self.logger.log_issue(insight)
                    self.cache.store_incident(insight)
                    self.redis_client.set(f"strategy_engine:research:{strategy_id}:{source}", str(insight), ex=604800)
                    await self.notify_training(insight)

            summary = {
                "type": "research_scraper_summary",
                "insight_count": len(insights),
                "timestamp": int(time.time()),
                "description": f"Scraped {len(insights)} AI research insights"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return insights
        except Exception as e:
            self.logger.log(f"Error scraping AI research: {e}")
            self.cache.store_incident({
                "type": "ai_lab_scraper_error",
                "timestamp": int(time.time()),
                "description": f"Error scraping AI research: {str(e)}"
            })
            return []

    async def notify_training(self, insight: Dict[str, Any]):
        """Notify Training Module of research insights."""
        self.logger.log(f"Notifying Training Module: {insight.get('description', 'unknown')}")
        self.redis_client.publish("training_module", str(insight))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of research scraper results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))