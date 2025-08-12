from typing import Dict, Any, List
import time
import pandas as pd
import json

class StrategyRegistry:
    def __init__(self, connection_manager, config: Dict[str, Any]):
        self.config = config
        self.connection_manager = connection_manager
        self.risk_profiles = self._load_risk_profiles()

    def _load_risk_profiles(self) -> Dict[str, Any]:
        """Load strategy risk profiles from config or JSON."""
        try:
            profile_path = self.config.get("risk_profile_path", "strategy_risk_profiles.json")
            with open(profile_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading risk profiles: {e}")
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
                # Store registration in Redis using connection manager
                redis_client = await self.connection_manager.get_redis_client()
                if redis_client:
                    redis_client.set(f"risk_management:strategy:{strategy_id}", str(registration), ex=604800)

            summary = {
                "type": "strategy_registration_summary",
                "registration_count": len(registrations),
                "timestamp": int(time.time()),
                "description": f"Registered {len(registrations)} strategies"
            }
            await self.notify_core(summary)
            return registrations
        except Exception as e:
            print(f"Error in strategy registry: {e}")
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of strategy registration results."""
        print(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("risk_management_output", str(issue))