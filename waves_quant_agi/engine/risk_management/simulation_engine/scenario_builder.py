from typing import Dict, Any, List
import redis
import pandas as pd
import numpy as np
from ...market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ...market_conditions.memory.incident_cache import IncidentCache

class ScenarioBuilder:
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
        self.volatility_spike = config.get("volatility_spike", 0.5)  # 50% volatility increase
        self.price_drop = config.get("price_drop", 0.2)  # 20% price drop

    async def generate_scenarios(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate adverse scenarios (e.g., black swans)."""
        try:
            scenarios = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                base_volatility = float(row.get("volatility", 0.1))
                base_price = float(row.get("price", 1.0))

                scenario = {
                    "type": "adverse_scenario",
                    "symbol": symbol,
                    "scenario": "black_swan",
                    "volatility": base_volatility * (1 + self.volatility_spike),
                    "price_drop": base_price * self.price_drop,
                    "timestamp": int(time.time()),
                    "description": f"Generated black swan scenario for {symbol}: Volatility {base_volatility * (1 + self.volatility_spike):.2f}, Price drop {base_price * self.price_drop:.2f}"
                }
                scenarios.append(scenario)
                self.logger.log_issue(scenario)
                self.cache.store_incident(scenario)
                self.redis_client.set(f"risk_management:scenario:{symbol}:black_swan", str(scenario), ex=604800)
                await self.notify_stress_test(scenario)

            summary = {
                "type": "scenario_summary",
                "scenario_count": len(scenarios),
                "timestamp": int(time.time()),
                "description": f"Generated {len(scenarios)} adverse scenarios"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return scenarios
        except Exception as e:
            self.logger.log(f"Error generating scenarios: {e}")
            self.cache.store_incident({
                "type": "scenario_builder_error",
                "timestamp": int(time.time()),
                "description": f"Error generating scenarios: {str(e)}"
            })
            return []

    async def notify_stress_test(self, scenario: Dict[str, Any]):
        """Notify StressTestRunner of generated scenarios."""
        self.logger.log(f"Notifying StressTestRunner: {scenario.get('description', 'unknown')}")
        self.redis_client.publish("stress_test_runner", str(scenario))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of scenario generation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))