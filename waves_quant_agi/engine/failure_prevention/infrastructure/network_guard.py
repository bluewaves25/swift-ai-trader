import asyncio
import requests
from typing import Dict, Any
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache

class NetworkGuard:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.latency_threshold = config.get("latency_threshold", 0.5)  # seconds
        self.check_urls = config.get("check_urls", ["https://api.binance.com/api/v3/ping"])
        self.check_interval = config.get("check_interval", 60)  # seconds

    async def monitor_network(self):
        """Monitor network latency and API availability."""
        while True:
            for url in self.check_urls:
                await self.check_network_health(url)
            await asyncio.sleep(self.check_interval)

    async def check_network_health(self, url: str):
        """Check network latency and API status."""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            latency = time.time() - start_time

            if response.status_code != 200:
                issue = {
                    "type": "network_api_failure",
                    "url": url,
                    "status_code": response.status_code,
                    "timestamp": int(time.time()),
                    "description": f"API {url} returned status {response.status_code}"
                }
                self.logger.log_issue(issue)
                self.cache.store_incident(issue)
                await self.notify_core(issue)
                return False

            if latency > self.latency_threshold:
                issue = {
                    "type": "network_latency",
                    "url": url,
                    "latency": latency,
                    "threshold": self.latency_threshold,
                    "timestamp": int(time.time()),
                    "description": f"Network latency {latency}s exceeds threshold {self.latency_threshold}s"
                }
                self.logger.log_issue(issue)
                self.cache.store_incident(issue)
                await self.notify_core(issue)
                return False
            return True
        except Exception as e:
            self.logger.log(f"Error checking network for {url}: {e}")
            self.cache.store_incident({
                "type": "network_guard_error",
                "url": url,
                "timestamp": int(time.time()),
                "description": f"Error checking network for {url}: {str(e)}"
            })
            return False

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of network issues."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent

    def start(self):
        """Start the network guard."""
        asyncio.run(self.monitor_network())