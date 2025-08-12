from typing import Dict, Any, List
import time
import pandas as pd
import numpy as np

class StressTestRunner:
    def __init__(self, connection_manager, config: Dict[str, Any]):
        self.config = config
        self.connection_manager = connection_manager
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
                # Store result in Redis using connection manager
                redis_client = await self.connection_manager.get_redis_client()
                if redis_client:
                    redis_client.set(f"risk_management:stress_test:{symbol}:{scenario}", str(result), ex=604800)
                    if result["description"].startswith("Stress test failed"):
                        await self.notify_execution(result)

            summary = {
                "type": "stress_test_summary",
                "result_count": len(test_results),
                "timestamp": int(time.time()),
                "description": f"Ran {len(test_results)} stress tests"
            }
            await self.notify_core(summary)
            return test_results
        except Exception as e:
            print(f"Error in stress test runner: {e}")
            return []

    async def notify_execution(self, result: Dict[str, Any]):
        """Notify Executions Agent of failed stress tests."""
        print(f"Notifying Executions Agent: {result.get('description', 'unknown')}")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("execution_agent", str(result))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of stress test results."""
        print(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("risk_management_output", str(issue))