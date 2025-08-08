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

class VisualRiskTrace:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.output_path = config.get("output_path", "risk_traces/")

    async def visualize_risk_decisions(self, risk_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Visualize risk decisions for transparency."""
        try:
            visuals = []
            if not MATPLOTLIB_AVAILABLE:
                self.logger.log("Warning: matplotlib not available, skipping risk trace visualizations")
                return visuals
                
            for risk_type in risk_data["type"].unique():
                type_data = risk_data[risk_data["type"] == risk_type]
                plt.figure(figsize=(12, 6))
                for symbol in type_data["symbol"].unique():
                    symbol_data = type_data[type_data["symbol"] == symbol]
                    plt.plot(symbol_data["timestamp"], symbol_data["risk_score"], label=symbol, marker='o')

                plt.title(f"Risk Trace: {risk_type}")
                plt.xlabel("Timestamp")
                plt.ylabel("Risk Score")
                plt.legend()
                plt.grid(True)
                output_file = f"{self.output_path}{risk_type}_risk_trace.png"
                plt.savefig(output_file)
                plt.close()

                visual = {
                    "type": "risk_trace_visual",
                    "risk_type": risk_type,
                    "output_file": output_file,
                    "timestamp": int(time.time()),
                    "description": f"Generated risk trace visualization for {risk_type}"
                }
                visuals.append(visual)
                self.logger.log_risk_assessment("assessment", visual)
                self.redis_client.set(f"risk_management:visual_risk_trace:{risk_type}", str(visual), ex=604800)

            summary = {
                "type": "risk_trace_summary",
                "visual_count": len(visuals),
                "timestamp": int(time.time()),
                "description": f"Generated {len(visuals)} risk trace visualizations"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return visuals
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of risk trace visualization results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))