from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ....logs.risk_management_logger import RiskManagementLogger

class EarningsReactionRisk:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.earnings_surprise_threshold = config.get("earnings_surprise_threshold", 0.05)  # 5% surprise
        self.volatility_tolerance = config.get("volatility_tolerance", 0.4)  # 40% volatility limit

    async def evaluate_risk(self, earnings_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Evaluate risk for earnings reaction trading strategy."""
        try:
            risk_decisions = []
            for _, row in earnings_data.iterrows():
                symbol = row.get("symbol", "SPY")
                earnings_surprise = float(row.get("earnings_surprise", 0.0))
                volatility = float(row.get("volatility", 0.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

                if abs(earnings_surprise) < self.earnings_surprise_threshold or volatility > self.volatility_tolerance:
                    decision = {
                        "type": "earnings_reaction_risk",
                        "symbol": symbol,
                        "earnings_surprise": earnings_surprise,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Earnings reaction denied for {symbol}: Surprise {earnings_surprise:.2f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }
                else:
                    decision = {
                        "type": "earnings_reaction_risk",
                        "symbol": symbol,
                        "earnings_surprise": earnings_surprise,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Earnings reaction approved for {symbol}: Surprise {earnings_surprise:.2f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }

                risk_decisions.append(decision)
                self.logger.log_risk_assessment("assessment", decision)
                decision)
                self.redis_client.set(f"risk_management:earnings_reaction:{symbol}", str(decision), ex=3600)
                if decision["description"].startswith("Earnings reaction approved"):
                    await self.notify_execution(decision)

            summary = {
                "type": "earnings_reaction_summary",
                "decision_count": len(risk_decisions),
                "timestamp": int(time.time()),
                "description": f"Evaluated {len(risk_decisions)} earnings reaction risks"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return risk_decisions
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_execution(self, decision: Dict[str, Any]):
        """Notify Executions Agent of approved earnings risk."""
        self.logger.log(f"Notifying Executions Agent: {decision.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(decision))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of earnings risk evaluation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))