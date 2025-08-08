from typing import Dict, Any
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache

class FallbackManager:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.fallbacks = config.get("fallbacks", {})  # e.g., {"broker": ["binance", "kraken"], "strategy": ["strat1", "strat2"]}
        self.active_fallbacks = {}

    async def activate_fallback(self, component: str, failed_id: str):
        """Activate fallback for a failed component (broker, strategy, etc.)."""
        try:
            available_fallbacks = self.fallbacks.get(component, [])
            if not available_fallbacks:
                self.logger.log(f"No fallbacks available for {component}")
                return False

            next_fallback = available_fallbacks[0]  # Simple: pick first available
            self.active_fallbacks[component] = next_fallback
            issue = {
                "type": f"{component}_fallback_activated",
                "failed_id": failed_id,
                "fallback_id": next_fallback,
                "timestamp": int(time.time()),
                "description": f"Activated fallback {next_fallback} for {component} {failed_id}"
            }
            self.logger.log_issue(issue)
            self.cache.store_incident(issue)
            await self.notify_core(issue)
            return True
        except Exception as e:
            self.logger.log(f"Error activating fallback for {component}: {e}")
            self.cache.store_incident({
                "type": f"{component}_fallback_error",
                "timestamp": int(time.time()),
                "description": f"Error activating fallback for {component}: {str(e)}"
            })
            return False

    async def revert_fallback(self, component: str):
        """Revert to primary component after resolution."""
        try:
            if component in self.active_fallbacks:
                issue = {
                    "type": f"{component}_fallback_reverted",
                    "fallback_id": self.active_fallbacks[component],
                    "timestamp": int(time.time()),
                    "description": f"Reverted fallback for {component}"
                }
                del self.active_fallbacks[component]
                self.logger.log_issue(issue)
                self.cache.store_incident(issue)
                await self.notify_core(issue)
        except Exception as e:
            self.logger.log(f"Error reverting fallback for {component}: {e}")

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of fallback actions."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        # Placeholder: Implement Redis publish or API call to Core Agent