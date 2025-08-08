from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ....logs.risk_management_logger import RiskManagementLogger

class AdaptiveQuoteRisk:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.quote_adjustment_threshold = config.get("quote_adjustment_threshold", 0.002)  # 0.2% min adjustment
        self.volatility_tolerance = config.get("volatility_tolerance", 0.15)  # 15% volatility limit

    async def evaluate_risk(self, quote_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Evaluate risk for adaptive quote market-making strategy."""
        try:
            risk_decisions = []
            for _, row in quote_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                quote_adjustment = float(row.get("quote_adjustment", 0.0))
                volatility = float(row.get("volatility", 0.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

                if quote_adjustment < self.quote_adjustment_threshold or volatility > self.volatility_tolerance:
                    decision = {
                        "type": "adaptive_quote_risk",
                        "symbol": symbol,
                        "quote_adjustment": quote_adjustment,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Adaptive quote denied for {symbol}: Adjustment {quote_adjustment:.4f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }
                else:
                    decision = {
                        "type": "adaptive_quote_risk",
                        "symbol": symbol,
                        "quote_adjustment": quote_adjustment,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Adaptive quote approved for {symbol}: Adjustment {quote_adjustment:.4f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }

                risk_decisions.append(decision)
                self.logger.log_risk_assessment("assessment", decision)
                decision)
                self.redis_client.set(f"risk_management:adaptive_quote:{symbol}", str(decision), ex=3600)
                if decision["description"].startswith("Adaptive quote approved"):
                    await self.notify_execution(decision)

            summary = {
                "type": "adaptive_quote_summary",
                "decision_count": len(risk_decisions),
                "timestamp": int(time.time()),
                "description": f"Evaluated {len(risk_decisions)} adaptive quote risks"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return risk_decisions
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_execution(self, decision: Dict[str, Any]):
        """Notify Executions Agent of approved adaptive quote risk."""
        self.logger.log(f"Notifying Executions Agent: {decision.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(decision))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of adaptive quote risk evaluation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))