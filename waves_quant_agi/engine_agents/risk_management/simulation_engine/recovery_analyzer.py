from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ..logs.risk_management_logger import RiskManagementLogger

class RecoveryAnalyzer:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.recovery_time_threshold = config.get("recovery_time_threshold", 86400)  # 1 day in seconds
        self.max_loss_threshold = config.get("max_loss_threshold", 0.1)  # 10% max loss

    async def analyze_recovery(self, stress_test_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Quantify recovery times post-stress scenarios."""
        try:
            recovery_results = []
            for _, row in stress_test_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                scenario = row.get("scenario", "unknown")
                simulated_loss = float(row.get("simulated_loss", 0.0))
                recovery_time = float(row.get("recovery_time", float('inf')))

                if simulated_loss > self.max_loss_threshold and recovery_time > self.recovery_time_threshold:
                    result = {
                        "type": "recovery_analysis",
                        "symbol": symbol,
                        "scenario": scenario,
                        "simulated_loss": simulated_loss,
                        "recovery_time": recovery_time,
                        "timestamp": int(time.time()),
                        "description": f"Recovery failed for {symbol} in {scenario}: Loss {simulated_loss:.2%}, Recovery time {recovery_time:.0f}s"
                    }
                else:
                    result = {
                        "type": "recovery_analysis",
                        "symbol": symbol,
                        "scenario": scenario,
                        "simulated_loss": simulated_loss,
                        "recovery_time": recovery_time,
                        "timestamp": int(time.time()),
                        "description": f"Recovery passed for {symbol} in {scenario}: Loss {simulated_loss:.2%}, Recovery time {recovery_time:.0f}s"
                    }

                recovery_results.append(result)
                self.logger.log_risk_assessment("assessment", result)
                self.redis_client.set(f"risk_management:recovery:{symbol}:{scenario}", str(result), ex=604800)
                if result["description"].startswith("Recovery failed"):
                    await self.notify_execution(result)

            summary = {
                "type": "recovery_analysis_summary",
                "result_count": len(recovery_results),
                "timestamp": int(time.time()),
                "description": f"Analyzed {len(recovery_results)} recovery times"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return recovery_results
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_execution(self, result: Dict[str, Any]):
        """Notify Executions Agent of failed recovery results."""
        self.logger.log(f"Notifying Executions Agent: {result.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(result))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of recovery analysis results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))