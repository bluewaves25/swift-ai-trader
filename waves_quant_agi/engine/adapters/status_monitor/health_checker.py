from typing import Dict, Any
import asyncio
import requests
from ..logs.broker_logger import BrokerLogger
from ..broker_integrations.base_adapter import BaseAdapter

class HealthChecker:
    def __init__(self, adapters: Dict[str, BaseAdapter], check_interval: int = 60):
        self.adapters = adapters
        self.check_interval = check_interval
        self.logger = BrokerLogger("health_checker")
        self.statuses = {name: "unknown" for name in adapters}

    async def check_broker(self, broker_name: str, adapter: BaseAdapter) -> str:
        """Check the health of a single broker."""
        try:
            # Placeholder: ping broker's health endpoint or test API call
            response = requests.get(f"https://api.{broker_name}.com/health", timeout=5)
            status = "up" if response.status_code == 200 else "down"
            self.logger.log_request("health_check", {"broker": broker_name, "status": status})
            return status
        except Exception as e:
            self.logger.log_request("health_check", {"broker": broker_name, "error": str(e)})
            return "down"

    async def monitor(self):
        """Continuously monitor all brokers."""
        while True:
            for name, adapter in self.adapters.items():
                self.statuses[name] = await self.check_broker(name, adapter)
            await asyncio.sleep(self.check_interval)

    def get_status(self, broker_name: str) -> str:
        """Get the current status of a broker."""
        return self.statuses.get(broker_name, "unknown")