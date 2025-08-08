from typing import Callable, Any, Optional
import asyncio
import time
from ..logs.broker_logger import BrokerLogger

class RetryHandler:
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.logger = BrokerLogger("retry_handler")

    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Optional[Any]:
        """Execute a function with exponential backoff retries."""
        attempt = 0
        delay = self.base_delay
        while attempt < self.max_retries:
            try:
                result = await func(*args, **kwargs)
                self.logger.log_request("retry", {"attempt": attempt, "success": True})
                return result
            except Exception as e:
                attempt += 1
                if attempt == self.max_retries:
                    self.logger.log_request("retry", {"attempt": attempt, "error": str(e), "success": False})
                    return None
                delay = min(delay * 2, self.max_delay)  # Exponential backoff
                self.logger.log_request("retry", {"attempt": attempt, "error": str(e), "delay": delay})
                await asyncio.sleep(delay)
        return None

    def adjust_retry_params(self, success_rate: float):
        """Adjust retry parameters based on success rate."""
        if success_rate < 0.5:
            self.max_retries = min(self.max_retries + 1, 5)
            self.base_delay = min(self.base_delay * 1.5, 5.0)
        elif success_rate > 0.8:
            self.max_retries = max(self.max_retries - 1, 2)
            self.base_delay = max(self.base_delay / 1.5, 0.5)
        self.logger.log_request("adjust_retry", {"success_rate": success_rate, "max_retries": self.max_retries, "base_delay": self.base_delay})