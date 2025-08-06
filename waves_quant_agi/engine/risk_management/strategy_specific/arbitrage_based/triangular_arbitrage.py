from typing import Dict, Any, List
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class TriangularArbitrageRisk:
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
        self.spread_threshold = config.get("spread_threshold", 0.001)  # 0.1% min spread
        self.slippage_tolerance = config.get("slippage_tolerance", 0.002)  # 0.2% max slippage

    async def evaluate_risk(self, arbitrage_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Evaluate risk for triangular arbitrage strategy."""
        try:
            risk_decisions = []
            for _, row in arbitrage_data.iterrows():
                symbol = row.get("symbol", "BTC/ETH/USD")
                spread = float(row.get("spread", 0.0))
                slippage = float(row.get("slippage", 0.0))
                fee_score = float(self.redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

                if spread < self.spread_threshold or slippage > self.slippage_tolerance or fee_score > spread:
                    decision = {
                        "type": "triangular_arbitrage_risk",
                        "symbol": symbol,
                        "spread": spread,
                        "slippage": slippage,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Triangular arbitrage denied for {symbol}: Spread {spread:.4f}, Slippage {slippage:.4f}, Fees {fee_score:.4f}"
                    }
                else:
                    decision = {
                        "type": "triangular_arbitrage_risk",
                        "symbol": symbol,
                        "spread": spread,
                        "slippage": slippage,
                        "fee_score": fee_score,
                        "timestamp": int(time.time()),
                        "description": f"Triangular arbitrage approved for {symbol}: Spread {spread:.4f}, Slippage {slippage:.4f}, Fees {fee_score:.4f}"
                    }

                risk_decisions.append(decision)
                self.logger.log_issue(decision)
                self.cache.store_incident(decision)
                self.redis_client.set(f"risk_management:triangular_arbitrage:{symbol}", str(decision), ex=3600)
                if decision["description"].startswith("Triangular arbitrage approved"):
                    await self.notify_execution(decision)

            summary = {
                "type": "triangular_arbitrage_summary",
                "decision_count": len(risk_decisions),
                "timestamp": int(time.time()),
                "description": f"Evaluated {len(risk_decisions)} triangular arbitrage risks"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return risk_decisions
        except Exception as e:
            self.logger.log(f"Error evaluating triangular arbitrage risk: {e}")
            self.cache.store_incident({
                "type": "triangular_arbitrage_risk_error",
                "timestamp": int(time.time()),
                "description": f"Error evaluating triangular arbitrage risk: {str(e)}"
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