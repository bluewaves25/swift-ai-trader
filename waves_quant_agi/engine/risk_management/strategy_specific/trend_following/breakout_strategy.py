from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class BreakoutStrategyRisk:
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
        self.breakout_strength_threshold = config.get("breakout_strength_threshold", 0.02)  # 2% breakout move
        self.volatility_tolerance = config.get("volatility_tolerance", 0.3)  # 30% volatility limit

    async def evaluate_risk(self, breakout_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Evaluate risk for breakout trading strategy."""
        try:
            risk_decisions = []
            for _, row in breakout_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                breakout_strength = float(row.get("breakout_strength", 0.0))
                volatility = float(row.get("volatility", 0.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

                if breakout_strength < self.breakout_strength_threshold or volatility > self.volatility_tolerance:
                    decision = {
                        "type": "breakout_strategy_risk",
                        "symbol": symbol,
                        "breakout_strength": breakout_strength,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Breakout strategy denied for {symbol}: Strength {breakout_strength:.4f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }
                else:
                    decision = {
                        "type": "breakout_strategy_risk",
                        "symbol": symbol,
                        "breakout_strength": breakout_strength,
                        "volatility": volatility,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Breakout strategy approved for {symbol}: Strength {breakout_strength:.4f}, Volatility {volatility:.2f}, Fees {fee_score:.4f}"
                    }

                risk_decisions.append(decision)
                self.logger.log_issue(decision)
                self.cache.store_incident(decision)
                self.redis_client.set(f"risk_management:breakout_strategy:{symbol}", str(decision), ex=3600)
                if decision["description"].startswith("Breakout strategy approved"):
                    await self.notify_execution(decision)

            summary = {
                "type": "breakout_strategy_summary",
                "decision_count": len(risk_decisions),
                "timestamp": int(time.time()),
                "description": f"Evaluated {len(risk_decisions)} breakout strategy risks"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return risk_decisions
        except Exception as e:
            self.logger.log(f"Error evaluating breakout strategy risk: {e}")
            self.cache.store_incident({
                "type": "breakout_strategy_risk_error",
                "timestamp": int(time.time()),
                "description": f"Error evaluating breakout strategy risk: {str(e)}"
            })
            return []

    async def notify_execution(self, decision: Dict[str, Any]):
        """Notify Executions Agent of approved breakout risk."""
        self.logger.log(f"Notifying Executions Agent: {decision.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(decision))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of breakout risk evaluation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))