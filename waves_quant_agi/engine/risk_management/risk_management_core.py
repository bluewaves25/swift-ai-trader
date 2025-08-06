from typing import Dict, Any, List
import redis
import pandas as pd
from .long_term.portfolio_diversifier import PortfolioDiversifier
from .long_term.capital_allocator import CapitalAllocator
from .short_term.real_time_risk_monitor import RealTimeRiskMonitor
from .quantum_risk_core.uncertainty_entropy_model import UncertaintyEntropyModel
from .audit_trails.visual_risk_trace import VisualRiskTrace
from ..market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ..market_conditions.memory.incident_cache import IncidentCache

class RiskManagementCore:
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
        self.diversifier = PortfolioDiversifier(config, logger, cache)
        self.allocator = CapitalAllocator(config, logger, cache)
        self.monitor = RealTimeRiskMonitor(config, logger, cache)
        self.entropy_model = UncertaintyEntropyModel(config, logger, cache)
        self.risk_trace = VisualRiskTrace(config, logger, cache)
        self.risk_threshold = config.get("risk_threshold", 0.05)  # 5% max risk

    async def evaluate_risk(self, strategy_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Orchestrate risk evaluation across submodules."""
        try:
            risk_decisions = []
            for _, row in strategy_data.iterrows():
                strategy_id = row.get("strategy_id", "unknown")
                symbol = row.get("symbol", "BTC/USD")
                position_size = float(row.get("position_size", 0.0))

                # Check diversification and allocation
                diversification_score = await self.diversifier.assess_diversification(strategy_data)
                allocation = await self.allocator.allocate_capital(strategy_data)
                if diversification_score < self.config.get("diversification_threshold", 0.7):
                    decision = {"status": "deny", "reason": "Insufficient diversification"}
                elif allocation["available_capital"] < position_size:
                    decision = {"status": "deny", "reason": "Insufficient capital allocation"}
                else:
                    # Check real-time risk and entropy
                    risk_score = await self.monitor.assess_risk(strategy_data)
                    entropy_score = await self.entropy_model.compute_entropy(strategy_data)
                    if risk_score > self.risk_threshold or entropy_score > self.config.get("entropy_threshold", 0.8):
                        decision = {"status": "deny", "reason": f"High risk ({risk_score:.2f}) or entropy ({entropy_score:.2f})"}
                    else:
                        decision = {"status": "approve", "reason": "Risk within limits"}

                risk_decision = {
                    "type": "risk_decision",
                    "strategy_id": strategy_id,
                    "symbol": symbol,
                    "status": decision["status"],
                    "risk_score": risk_score,
                    "entropy_score": entropy_score,
                    "timestamp": int(time.time()),
                    "description": f"Risk decision for {strategy_id} ({symbol}): {decision['reason']}"
                }
                risk_decisions.append(risk_decision)
                self.logger.log_issue(risk_decision)
                self.cache.store_incident(risk_decision)
                self.redis_client.set(f"risk_management:decision:{strategy_id}", str(risk_decision), ex=3600)
                await self.risk_trace.log_decision(risk_decision)
                if risk_decision["status"] == "approve":
                    await self.notify_execution(risk_decision)

            summary = {
                "type": "risk_evaluation_summary",
                "decision_count": len(risk_decisions),
                "timestamp": int(time.time()),
                "description": f"Evaluated {len(risk_decisions)} risk decisions"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return risk_decisions
        except Exception as e:
            self.logger.log(f"Error evaluating risk: {e}")
            self.cache.store_incident({
                "type": "risk_management_core_error",
                "timestamp": int(time.time()),
                "description": f"Error evaluating risk: {str(e)}"
            })
            return []

    async def notify_execution(self, decision: Dict[str, Any]):
        """Notify Executions Agent of approved risk decision."""
        self.logger.log(f"Notifying Executions Agent: {decision.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(decision))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of risk evaluation results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))