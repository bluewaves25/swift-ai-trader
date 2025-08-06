from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class CointegrationModelRisk:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.cointegration_p_value = config.get("cointegration_p_value", 0.05)  # 5% significance
        self.spread_volatility_tolerance = config.get("spread_volatility_tolerance", 0.25)  # 25% volatility limit

    async def evaluate_risk(self, cointegration_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Evaluate risk for cointegration-based strategy."""
        try:
            risk_decisions = []
            for _, row in cointegration_data.iterrows():
                symbol_pair = row.get("symbol_pair", "BTC/ETH")
                p_value = float(row.get("cointegration_p_value", 1.0))
                spread_volatility = float(row.get("spread_volatility", 0.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol_pair}:fee_score") or 0.0)

                if p_value > self.cointegration_p_value or spread_volatility > self.spread_volatility_tolerance:
                    decision = {
                        "type": "cointegration_risk",
                        "symbol_pair": symbol_pair,
                        "p_value": p_value,
                        "spread_volatility": spread_volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Cointegration denied for {symbol_pair}: P-value {p_value:.4f}, Spread volatility {spread_volatility:.2f}, Fees {fee_score:.4f}"
                    }
                else:
                    decision = {
                        "type": "cointegration_risk",
                        "symbol_pair": symbol_pair,
                        "p_value": p_value,
                        "spread_volatility": spread_volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Cointegration approved for {symbol_pair}: P-value {p_value:.4f}, Spread volatility {spread_volatility:.2f}, Fees {fee_score:.4f}"
                    }

                risk_decisions.append(decision)
                self.logger.log_issue(decision)
                self.cache.store_incident(decision)
                self.redis_client.set(f"risk_management:cointegration:{symbol_pair}", str(decision), ex=3600)
                if decision["description"].startswith("Cointegration approved"):
                    await self.notify_execution(decision)

            summary = {
                "type": "cointegration_summary",
                "decision_count": len(risk_decisions),
                "timestamp": int(time.time()),
                "description": f"Evaluated {len(risk_decisions)} cointegration risks"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return risk_decisions
        except Exception as e:
            self.logger.log(f"Error evaluating cointegration risk: {e}")
            self.cache.store_incident({
                "type": "cointegration_risk_error",
                "timestamp": int(time.time()),
                "description": f"Error evaluating cointegration risk: {str(e)}"
            })
            return []

    async def notify_execution(self, decision: Dict[str, Any]):
        """Notify Executions Agent of approved cointegration risk."""
        self.logger.log(f"Notifying Executions Agent: {decision.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(decision))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of cointegration risk evaluation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))