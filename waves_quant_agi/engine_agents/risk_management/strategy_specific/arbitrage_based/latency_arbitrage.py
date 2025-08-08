from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ....logs.risk_management_logger import RiskManagementLogger

class LatencyArbitrageRisk:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.latency_threshold = config.get("latency_threshold", 10.0)  # 10ms max latency
        self.price_diff_threshold = config.get("price_diff_threshold", 0.001)  # 0.1% min price diff

    async def evaluate_risk(self, arbitrage_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Evaluate risk for latency arbitrage strategy."""
        try:
            risk_decisions = []
            for _, row in arbitrage_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                latency = float(row.get("latency", 0.0))
                price_diff = float(row.get("price_diff", 0.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

                if latency > self.latency_threshold or price_diff < self.price_diff_threshold or fee_score > price_diff:
                    decision = {
                        "type": "latency_arbitrage_risk",
                        "symbol": symbol,
                        "latency": latency,
                        "price_diff": price_diff,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Latency arbitrage denied for {symbol}: Latency {latency:.2f}ms, Price diff {price_diff:.4f}, Fees {fee_score:.4f}"
                    }
                else:
                    decision = {
                        "type": "latency_arbitrage_risk",
                        "symbol": symbol,
                        "latency": latency,
                        "price_diff": price_diff,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Latency arbitrage approved for {symbol}: Latency {latency:.2f}ms, Price diff {price_diff:.4f}, Fees {fee_score:.4f}"
                    }

                risk_decisions.append(decision)
                self.logger.log_risk_assessment("assessment", decision)
                decision)
                self.redis_client.set(f"risk_management:latency_arbitrage:{symbol}", str(decision), ex=3600)
                if decision["description"].startswith("Latency arbitrage approved"):
                    await self.notify_execution(decision)

            summary = {
                "type": "latency_arbitrage_summary",
                "decision_count": len(risk_decisions),
                "timestamp": int(time.time()),
                "description": f"Evaluated {len(risk_decisions)} latency arbitrage risks"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return risk_decisions
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_execution(self, decision: Dict[str, Any]):
        """Notify Executions Agent of approved arbitrage risk."""
        self.logger.log(f"Notifying Executions Agent: {decision.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(decision))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of arbitrage risk evaluation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))