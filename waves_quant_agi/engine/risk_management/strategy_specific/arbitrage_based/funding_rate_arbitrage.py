from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class FundingRateArbitrageRisk:
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
        self.funding_rate_threshold = config.get("funding_rate_threshold", 0.0005)  # 0.05% min rate
        self.exposure_limit = config.get("exposure_limit", 0.1)  # 10% max exposure

    async def evaluate_risk(self, arbitrage_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Evaluate risk for funding rate arbitrage strategy."""
        try:
            risk_decisions = []
            for _, row in arbitrage_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                funding_rate = float(row.get("funding_rate", 0.0))
                exposure = float(row.get("exposure", 0.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

                if funding_rate < self.funding_rate_threshold or exposure > self.exposure_limit or fee_score > funding_rate:
                    decision = {
                        "type": "funding_rate_arbitrage_risk",
                        "symbol": symbol,
                        "funding_rate": funding_rate,
                        "exposure": exposure,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Funding rate arbitrage denied for {symbol}: Rate {funding_rate:.4f}, Exposure {exposure:.2%}, Fees {fee_score:.4f}"
                    }
                else:
                    decision = {
                        "type": "funding_rate_arbitrage_risk",
                        "symbol": symbol,
                        "funding_rate": funding_rate,
                        "exposure": exposure,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Funding rate arbitrage approved for {symbol}: Rate {funding_rate:.4f}, Exposure {exposure:.2%}, Fees {fee_score:.4f}"
                    }

                risk_decisions.append(decision)
                self.logger.log_issue(decision)
                self.cache.store_incident(decision)
                self.redis_client.set(f"risk_management:funding_rate_arbitrage:{symbol}", str(decision), ex=3600)
                if decision["description"].startswith("Funding rate arbitrage approved"):
                    await self.notify_execution(decision)

            summary = {
                "type": "funding_rate_arbitrage_summary",
                "decision_count": len(risk_decisions),
                "timestamp": int(time.time()),
                "description": f"Evaluated {len(risk_decisions)} funding rate arbitrage risks"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return risk_decisions
        except Exception as e:
            self.logger.log(f"Error evaluating funding rate arbitrage risk: {e}")
            self.cache.store_incident({
                "type": "funding_rate_arbitrage_risk_error",
                "timestamp": int(time.time()),
                "description": f"Error evaluating funding rate arbitrage risk: {str(e)}"
            })
            return []

    async def notify_execution(self, decision: Dict[str, Any]):
        """Notify Executions Agent of approved arbitrage risk."""
        self.logger.log(f"Notifying Executions Agent: {decision.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(decision))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of arbitrage risk evaluation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))