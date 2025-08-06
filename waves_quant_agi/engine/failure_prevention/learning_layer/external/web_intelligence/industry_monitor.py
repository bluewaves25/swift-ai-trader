import requests
from typing import Dict, Any, List
from ...logs.failure_agent_logger import FailureAgentLogger
from ...memory.incident_cache import IncidentCache

class IndustryMonitor:
    def __init__(self, api_key: str, sources: List[str], logger: FailureAgentLogger, cache: IncidentCache):
        self.api_key = api_key
        self.sources = sources  # e.g., ["newsapi.org"]
        self.logger = logger
        self.cache = cache
        self.headers = {"User-Agent": "FailurePreventionAgent/1.0"}

    def fetch_industry_incidents(self) -> List[Dict[str, Any]]:
        """Fetch industry news for broker or market incidents."""
        try:
            incidents = []
            for source in self.sources:
                url = f"https://newsapi.org/v2/everything?q=trading+outage+OR+broker+failure&sources={source}&apiKey={self.api_key}"
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                articles = response.json().get("articles", [])
                for article in articles[:5]:  # Limit to recent articles
                    incidents.append({
                        "source": source,
                        "title": article.get("title", "")[:500],
                        "type": "industry_incident",
                        "timestamp": int(time.time()),
                        "description": article.get("description", "")[:500] or article.get("title", "")
                    })
                    self.cache.store_incident(incidents[-1])
                    self.logger.log(f"Fetched industry incident: {incidents[-1]['title']}")
            return incidents
        except Exception as e:
            self.logger.log(f"Error fetching industry incidents: {e}")
            return []