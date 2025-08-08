from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ....logs.risk_management_logger import RiskManagementLogger

class MovingAverageCrossoverRisk:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.signal_strength_threshold = config.get("signal_strength_threshold", 0.01)  # 1% MA crossover signal
        self.volatility_tolerance = config.get("volatility_tolerance", 0.3)  # 30% volatility limit

    async def evaluate_risk(self, ma_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Evaluate risk for moving average crossover strategy."""
        try:
            risk_decisions = []
            for _, row in ma_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                signal_strength = float(row.get("signal_strength", 0.0))
                volatility = float(row.get("volatility", 0.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

                if signal_strength < self.signal_strength_threshold or volatility > self.volatility_tolerance:
                    decision = {
                        "type": "ma_crossover_risk",
                        "symbol": symbol,
                        "signal_strength": signal_strength,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"MA crossover denied for {symbol}: Signal {signal_strength:.4f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }
                else:
                    decision = {
                        "type": "ma_crossover_risk",
                        "symbol": symbol,
                        "signal_strength": signal_strength,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"MA crossover approved for {symbol}: Signal {signal_strength:.4f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }

                risk_decisions.append(decision)
                self.logger.log_risk_assessment("assessment", decision)
                decision)
                self.redis_client.set(f"risk_management:ma_crossover:{symbol}", str(decision), ex=3600)
                if decision["description"].startswith("MA crossover approved"):
                    await self.notify_execution(decision)

            summary = {
                "type": "ma_crossover_summary",
                "decision_count": len(risk_decisions),
                "timestamp": int(time.time()),
                "description": f"Evaluated {len(risk_decisions)} MA crossover risks"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return risk_decisions
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_execution(self, decision: Dict[str, Any]):
        """Notify Executions Agent of approved MA crossover risk."""
        self.logger.log(f"Notifying Executions Agent: {decision.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(decision))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of MA crossover risk evaluation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))