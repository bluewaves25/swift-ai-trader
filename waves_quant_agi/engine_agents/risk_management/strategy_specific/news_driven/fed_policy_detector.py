from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ....logs.risk_management_logger import RiskManagementLogger

class FedPolicyDetectorRisk:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.policy_impact_threshold = config.get("policy_impact_threshold", 0.6)  # 60% impact confidence
        self.volatility_tolerance = config.get("volatility_tolerance", 0.4)  # 40% volatility limit

    async def evaluate_risk(self, policy_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Evaluate risk for Fed policy-driven trading strategy."""
        try:
            risk_decisions = []
            for _, row in policy_data.iterrows():
                symbol = row.get("symbol", "USD/JPY")
                policy_impact = float(row.get("policy_impact_score", 0.0))
                volatility = float(row.get("volatility", 0.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

                if policy_impact < self.policy_impact_threshold or volatility > self.volatility_tolerance:
                    decision = {
                        "type": "fed_policy_risk",
                        "symbol": symbol,
                        "policy_impact": policy_impact,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Fed policy denied for {symbol}: Impact {policy_impact:.2f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }
                else:
                    decision = {
                        "type": "fed_policy_risk",
                        "symbol": symbol,
                        "policy_impact": policy_impact,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Fed policy approved for {symbol}: Impact {policy_impact:.2f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }

                risk_decisions.append(decision)
                self.logger.log_risk_assessment("assessment", decision)
                decision)
                self.redis_client.set(f"risk_management:fed_policy:{symbol}", str(decision), ex=3600)
                if decision["description"].startswith("Fed policy approved"):
                    await self.notify_execution(decision)

            summary = {
                "type": "fed_policy_summary",
                "decision_count": len(risk_decisions),
                "timestamp": int(time.time()),
                "description": f"Evaluated {len(risk_decisions)} Fed policy risks"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return risk_decisions
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_execution(self, decision: Dict[str, Any]):
        """Notify Executions Agent of approved Fed policy risk."""
        self.logger.log(f"Notifying Executions Agent: {decision.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(decision))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of Fed policy risk evaluation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))