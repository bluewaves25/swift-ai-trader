from typing import Dict, Any, List
import redis
import pandas as pd
import json
from ..market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ..market_conditions.memory.incident_cache import IncidentCache

class StrategyRegistry:
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
        self.risk_profiles = self._load_risk_profiles()

    def _load_risk_profiles(self) -> Dict[str, Any]:
        """Load strategy risk profiles from config or JSON."""
        try:
            profile_path = self.config.get("risk_profile_path", "strategy_risk_profiles.json")
            with open(profile_path, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.log(f"Error loading risk profiles: {e}")
            return {
                "arbitrage_based": {"max_drawdown": 0.03, "volatility_tolerance": 0.2},
                "trend_following": {"max_drawdown": 0.05, "volatility_tolerance": 0.3},
                "statistical_arbitrage": {"max_drawdown": 0.04, "volatility_tolerance": 0.25},
                "news_driven": {"max_drawdown": 0.06, "volatility_tolerance": 0.4},
                "market_making": {"max_drawdown": 0.02, "volatility_tolerance": 0.15},
                "htf": {"max_drawdown": 0.07, "volatility_tolerance": 0.5}
            }

    async def register_strategy(self, strategy_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Dynamically map strategies to risk profiles."""
        try:
            registrations = []
            for _, row in strategy_data.iterrows():
                strategy_id = row.get("strategy_id", "unknown")
                strategy_type = row.get("strategy_type", "unknown")
                symbol = row.get("symbol", "BTC/USD")

                risk_profile = self.risk_profiles.get(strategy_type, {"max_drawdown": 0.05, "volatility_tolerance": 0.3})
                registration = {
                    "type": "strategy_registration",
                    "strategy_id": strategy_id,
                    "strategy_type": strategy_type,
                    "symbol": symbol,
                    "risk_profile": risk_profile,
                    "timestamp": int(time.time()),
                    "description": f"Registered {strategy_id} ({strategy_type}) for {symbol}"
                }
                registrations.append(registration)
                self.logger.log_issue(registration)
                self.cache.store_incident(registration)
                self.redis_client.set(f"risk_management:strategy:{strategy_id}", str(registration), ex=604800)

            summary = {
                "type": "strategy_registration_summary",
                "registration_count": len(registrations),
                "timestamp": int(time.time()),
                "description": f"Registered {len(registrations)} strategies"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return registrations
        except Exception as e:
            self.logger.log(f"Error registering strategy: {e}")
            self.cache.store_incident({
                "type": "strategy_registry_error",
                "timestamp": int(time.time()),
                "description": f"Error registering strategy: {str(e)}"
            })
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of strategy registration results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))