from typing import Dict, Any, List
import redis
import pandas as pd
import numpy as np
from ...market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ...market_conditions.memory.incident_cache import IncidentCache

class StressTestRunner:
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
        self.loss_threshold = config.get("loss_threshold", 0.1)  # 10% max loss
        self.num_simulations = config.get("num_simulations", 1000)

    async def run_stress_tests(self, scenario_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Run historical and synthetic stress tests."""
        try:
            test_results = []
            for _, row in scenario_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                scenario = row.get("scenario", "market_crash")
                historical_loss = float(row.get("historical_loss", 0.0))
                synthetic_loss = np.random.normal(loc=historical_loss, scale=0.05, size=self.num_simulations).mean()

                if synthetic_loss > self.loss_threshold:
                    result = {
                        "type": "stress_test",
                        "symbol": symbol,
                        "scenario": scenario,
                        "synthetic_loss": synthetic_loss,
                        "timestamp": int(time.time()),
                        "description": f"Stress test failed for {symbol} in {scenario}: Loss {synthetic_loss:.2%}"
                    }
                else:
                    result = {
                        "type": "stress_test",
                        "symbol": symbol,
                        "scenario": scenario,
                        "synthetic_loss": synthetic_loss,
                        "timestamp": int(time.time()),
                        "description": f"Stress test passed for {symbol} in {scenario}: Loss {synthetic_loss:.2%}"
                    }

                test_results.append(result)
                self.logger.log_issue(result)
                self.cache.store_incident(result)
                self.redis_client.set(f"risk_management:stress_test:{symbol}:{scenario}", str(result), ex=604800)
                if result["description"].startswith("Stress test failed"):
                    await self.notify_execution(result)

            summary = {
                "type": "stress_test_summary",
                "result_count": len(test_results),
                "timestamp": int(time.time()),
                "description": f"Ran {len(test_results)} stress tests"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return test_results
        except Exception as e:
            self.logger.log(f"Error running stress tests: {e}")
            self.cache.store_incident({
                "type": "stress_test_runner_error",
                "timestamp": int(time.time()),
                "description": f"Error running stress tests: {str(e)}"
            })
            return []

    async def notify_execution(self, result: Dict[str, Any]):
        """Notify Executions Agent of failed stress tests."""
        self.logger.log(f"Notifying Executions Agent: {result.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(result))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of stress test results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))