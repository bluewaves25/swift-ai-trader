from typing import Dict, Any
import requests
import time
from ..logs.broker_logger import BrokerLogger

class APIMonitor:
    def __init__(self, brokers: Dict[str, str], check_interval: int = 3600):
        self.brokers = brokers  # Dict of broker_name: api_doc_url
        self.check_interval = check_interval
        self.logger = BrokerLogger("api_monitor")
        self.api_versions = {name: None for name in brokers}

    async def check_api_updates(self):
        """Check for API updates for all brokers."""
        while True:
            for broker_name, doc_url in self.brokers.items():
                try:
                    response = requests.get(doc_url, timeout=10)
                    response.raise_for_status()
                    current_version = response.headers.get('X-API-Version', response.text[:50])
                    if self.api_versions[broker_name] and self.api_versions[broker_name] != current_version:
                        self.logger.log_request("api_update", {"broker": broker_name, "new_version": current_version})
                        self.notify_update(broker_name, current_version)
                    self.api_versions[broker_name] = current_version
                except Exception as e:
                    self.logger.log_request("api_check", {"broker": broker_name, "error": str(e)})
            await asyncio.sleep(self.check_interval)

    def notify_update(self, broker_name: str, new_version: str):
        """Notify about API version change."""
        self.logger.log_request("notify_update", {"broker": broker_name, "new_version": new_version})
        # Placeholder: Implement notification logic (e.g., alert other components)