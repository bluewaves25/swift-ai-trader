from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ....logs.risk_management_logger import RiskManagementLogger

class MomentumRiderRisk:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.momentum_threshold = config.get("momentum_threshold", 0.015)  # 1.5% momentum strength
        self.volatility_tolerance = config.get("volatility_tolerance", 0.3)  # 30% volatility limit

    async def evaluate_risk(self, momentum_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Evaluate risk for momentum rider strategy."""
        try:
            risk_decisions = []
            for _, row in momentum_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                momentum_strength = float(row.get("momentum_strength", 0.0))
                volatility = float(row.get("volatility", 0.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

                if momentum_strength < self.momentum_threshold or volatility > self.volatility_tolerance:
                    decision = {
                        "type": "momentum_rider_risk",
                        "symbol": symbol,
                        "momentum_strength": momentum_strength,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Momentum rider denied for {symbol}: Momentum {momentum_strength:.4f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }
                else:
                    decision = {
                        "type": "momentum_rider_risk",
                        "symbol": symbol,
                        "momentum_strength": momentum_strength,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Momentum rider approved for {symbol}: Momentum {momentum_strength:.4f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }

                risk_decisions.append(decision)
                self.logger.log_risk_assessment("assessment", decision)
                decision)
                self.redis_client.set(f"risk_management:momentum_rider:{symbol}", str(decision), ex=3600)
                if decision["description"].startswith("Momentum rider approved"):
                    await self.notify_execution(decision)

            summary = {
                "type": "momentum_rider_summary",
                "decision_count": len(risk_decisions),
                "timestamp": int(time.time()),
                "description": f"Evaluated {len(risk_decisions)} momentum rider risks"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return risk_decisions
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_execution(self, decision: Dict[str, Any]):
        """Notify Executions Agent of approved momentum risk."""
        self.logger.log(f"Notifying Executions Agent: {decision.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(decision))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of momentum risk evaluation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))