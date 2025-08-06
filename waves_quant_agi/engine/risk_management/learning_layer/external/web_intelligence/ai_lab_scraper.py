from typing import Dict, Any, List
import redis
import pandas as pd
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
        self.relevance_threshold = config.get("relevance_threshold", 0.7)  # 70% relevance score

    async def scrape_research(self, web_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Scrape AI research for risk model enhancements."""
        try:
            research_findings = []
            for _, row in web_data.iterrows():
                source = row.get("source", "unknown")
                relevance_score = float(row.get("relevance_score", 0.0))
                research_content = row.get("content", "")

                if relevance_score >= self.relevance_threshold:
                    finding = {
                        "type": "ai_research_finding",
                        "source": source,
                        "relevance_score": relevance_score,
                        "content_summary": research_content[:100],
                        "timestamp": int(time.time()),
                        "description": f"Relevant AI research found from {source}: Relevance {relevance_score:.2f}"
                    }
                    research_findings.append(finding)
                    self.logger.log_issue(finding)
                    self.cache.store_incident(finding)
                    self.redis_client.set(f"risk_management:ai_research:{source}", str(finding), ex=604800)
                    await self.notify_learning(finding)
                else:
                    finding = {
                        "type": "ai_research_finding",
                        "source": source,
                        "relevance_score": relevance_score,
                        "content_summary": research_content[:100],
                        "timestamp": int(time.time()),
                        "description": f"Irrelevant AI research from {source}: Relevance {relevance_score:.2f}"
                    }
                    research_findings.append(finding)
                    self.logger.log_issue(finding)
                    self.cache.store_incident(finding)

            summary = {
                "type": "ai_research_summary",
                "finding_count": len(research_findings),
                "timestamp": int(time.time()),
                "description": f"Scraped {len(research_findings)} AI research findings"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return research_findings
        except Exception as e:
            self.logger.log(f"Error scraping AI research: {e}")
            self.cache.store_incident({
                "type": "ai_lab_scraper_error",
                "timestamp": int(time.time()),
                "description": f"Error scraping AI research: {str(e)}"
            })
            return []

    async def notify_learning(self, finding: Dict[str, Any]):
        """Notify Learning Layer of relevant research findings."""
        self.logger.log(f"Notifying Learning Layer: {finding.get('description', 'unknown')}")
        self.redis_client.publish("learning_layer", str(finding))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of research scraping results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))