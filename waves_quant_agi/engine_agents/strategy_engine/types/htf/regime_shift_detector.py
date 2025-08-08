from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ....market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ....market_conditions.memory.incident_cache import IncidentCache

class RegimeShiftDetector:
    def __init__(self, config: Dict[str, Any], logger: StrategyEngineLogger):
        self.config = config
        self.logger = logger
                self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.regime_change_threshold = config.get("regime_change_threshold", 0.75)  # Regime shift confidence

    async def detect_regime_shift(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect market regime shifts for high time frame trading."""
        try:
            opportunities = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "S&P500")
                regime_score = float(row.get("regime_score", 0.0))
                prev_regime = row.get("prev_regime", "neutral")
                current_regime = row.get("current_regime", "neutral")

                if regime_score > self.regime_change_threshold and current_regime != prev_regime:
                    signal = "buy" if current_regime == "bullish" else "sell" if current_regime == "bearish" else "hold"
                    opportunity = {
                        "type": "regime_shift_detector",
                        "symbol": symbol,
                        "signal": signal,
                        "regime_score": regime_score,
                        "current_regime": current_regime,
                        "timestamp": int(time.time()),
                        "description": f"Regime shift for {symbol}: {prev_regime} to {current_regime}, Score {regime_score:.2f}"
                    }
                    opportunities.append(opportunity)
                    self.logger.log_strategy_deployment("deployment", opportunity)
                    opportunity)
                    self.redis_client.set(f"strategy_engine:regime_shift:{symbol}", str(opportunity), ex=3600)
                    await self.notify_execution(opportunity)

            summary = {
                "type": "regime_shift_summary",
                "opportunity_count": len(opportunities),
                "timestamp": int(time.time()),
                "description": f"Detected {len(opportunities)} regime shift signals"
            }
            self.logger.log_strategy_deployment("deployment", summary)
            summary)
            await self.notify_core(summary)
            return opportunities
        except Exception as e:
            self.logger.log(f"Error detecting regime shift: {e}")
            {
                "type": "regime_shift_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting regime shift: {str(e)}"
            })
            return []

    async def notify_execution(self, opportunity: Dict[str, Any]):
        """Notify Executions Agent of regime shift signal."""
        self.logger.log(f"Notifying Executions Agent: {opportunity.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(opportunity))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of regime shift results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("strategy_engine_output", str(issue))