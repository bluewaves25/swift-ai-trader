from typing import Dict, Any, List
import redis
import json
import pandas as pd
import asyncio

class CounterfactualSimulator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.impact_threshold = config.get("impact_threshold", 0.1)  # 10% potential impact

    async def simulate_counterfactuals(self, rejected_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Simulate 'what-if' scenarios for rejected validations."""
        try:
            simulations = []
            for _, row in rejected_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                reason = row.get("reason", "unknown")
                size = float(row.get("size", 0.0))
                impact_score = float(row.get("impact_score", 0.0))

                if impact_score >= self.impact_threshold:
                    simulation = {
                        "type": "counterfactual_simulation",
                        "symbol": symbol,
                        "reason": reason,
                        "impact_score": impact_score,
                        "timestamp": int(pd.Timestamp.now().timestamp()),
                        "description": f"Simulated counterfactual for {symbol}: {reason}, Impact {impact_score:.2f}"
                    }
                    simulations.append(simulation)
                    self.redis_client.lpush(f"validation:simulation:{symbol}", json.dumps(simulation), ex=604800)
                    await self.notify_retraining(simulation)

            summary = {
                "type": "simulation_summary",
                "simulation_count": len(simulations),
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Simulated {len(simulations)} counterfactual scenarios"
            }
            self.redis_client.set("validation:simulation_summary", json.dumps(summary), ex=604800)
            await self.notify_core(summary)
            return simulations
        except Exception as e:
            self.redis_client.lpush("validation:errors", json.dumps({
                "type": "counterfactual_simulator_error",
                "timestamp": int(pd.Timestamp.now().timestamp()),
                "description": f"Error simulating counterfactuals: {str(e)}"
            }))
            return []

    async def notify_retraining(self, simulation: Dict[str, Any]):
        """Notify retraining loop of simulation results."""
        self.redis_client.publish("retraining_loop", json.dumps(simulation))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of simulation results."""
        self.redis_client.publish("validation_output", json.dumps(issue))