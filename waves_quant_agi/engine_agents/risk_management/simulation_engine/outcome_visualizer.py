from typing import Dict, Any, List
import time
import redis
import pandas as pd
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
from ..logs.risk_management_logger import RiskManagementLogger

class OutcomeVisualizer:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.output_path = config.get("output_path", "stress_test_visuals/")

    async def visualize_results(self, stress_test_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Visualize stress test results for risk analysis."""
        try:
            visuals = []
            if not MATPLOTLIB_AVAILABLE:
                self.logger.log("Warning: matplotlib not available, skipping visualizations")
                return visuals
                
            for scenario in stress_test_data["scenario"].unique():
                scenario_data = stress_test_data[stress_test_data["scenario"] == scenario]
                plt.figure(figsize=(10, 6))
                for symbol in scenario_data["symbol"].unique():
                    symbol_data = scenario_data[scenario_data["symbol"] == symbol]
                    plt.plot(symbol_data["timestamp"], symbol_data["simulated_loss"], label=symbol)

                plt.title(f"Stress Test: {scenario}")
                plt.xlabel("Timestamp")
                plt.ylabel("Simulated Loss (%)")
                plt.legend()
                plt.grid(True)
                output_file = f"{self.output_path}{scenario}_stress_test.png"
                plt.savefig(output_file)
                plt.close()

                visual = {
                    "type": "visualization",
                    "scenario": scenario,
                    "output_file": output_file,
                    "timestamp": int(time.time()),
                    "description": f"Generated stress test visualization for {scenario}"
                }
                visuals.append(visual)
                self.logger.log_risk_assessment("assessment", visual)
                self.redis_client.set(f"risk_management:visualization:{scenario}", str(visual), ex=604800)

            summary = {
                "type": "visualization_summary",
                "visual_count": len(visuals),
                "timestamp": int(time.time()),
                "description": f"Generated {len(visuals)} stress test visualizations"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return visuals
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of visualization results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))