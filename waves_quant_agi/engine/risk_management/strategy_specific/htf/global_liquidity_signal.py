from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class GlobalLiquiditySignalRisk:
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
        self.liquidity_score_threshold = config.get("liquidity_score_threshold", 0.6)  # 60% liquidity confidence
        self.volatility_tolerance = config.get("volatility_tolerance", 0.5)  # 50% volatility limit

    async def evaluate_risk(self, liquidity_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Evaluate risk for global liquidity-driven strategy."""
        try:
            risk_decisions = []
            for _, row in liquidity_data.iterrows():
                symbol = row.get("symbol", "XAU/USD")
                liquidity_score = float(row.get("liquidity_score", 0.0))
                volatility = float(row.get("volatility", 0.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

                if liquidity_score < self.liquidity_score_threshold or volatility > self.volatility_tolerance:
                    decision = {
                        "type": "global_liquidity_risk",
                        "symbol": symbol,
                        "liquidity_score": liquidity_score,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Global liquidity denied for {symbol}: Liquidity {liquidity_score:.2f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }
                else:
                    decision = {
                        "type": "global_liquidity_risk",
                        "symbol": symbol,
                        "liquidity_score": liquidity_score,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Global liquidity approved for {symbol}: Liquidity {liquidity_score:.2f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }

                risk_decisions.append(decision)
                self.logger.log_issue(decision)
                self.cache.store_incident(decision)
                self.redis_client.set(f"risk_management:global_liquidity:{symbol}", str(decision), ex=3600)
                if decision["description"].startswith("Global liquidity approved"):
                    await self.notify_execution(decision)

            summary = {
                "type": "global_liquidity_summary",
                "decision_count": len(risk_decisions),
                "timestamp": int(time.time()),
                "description": f"Evaluated {len(risk_decisions)} global liquidity risks"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return risk_decisions
        except Exception as e:
            self.logger.log(f"Error evaluating global liquidity risk: {e}")
            self.cache.store_incident({
                "type": "global_liquidity_risk_error",
                "timestamp": int(time.time()),
                "description": f"Error evaluating global liquidity risk: {str(e)}"
            })
            return []

    async def notify_execution(self, decision: Dict[str, Any]):
        """Notify Executions Agent of approved global liquidity risk."""
        self.logger.log(f"Notifying Executions Agent: {decision.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(decision))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of global liquidity risk evaluation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))