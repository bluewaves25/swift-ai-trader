from typing import Dict, Any, List
import redis
import pandas as pd
import numpy as np
from ..market_conditions.logs.failure_agent_logger import FailureAgentLogger
from ..market_conditions.memory.incident_cache import IncidentCache

class BlackSwanGuard:
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
        self.volatility_spike_threshold = config.get("volatility_spike_threshold", 3.0)  # 3x std dev
        self.liquidity_drop_threshold = config.get("liquidity_drop_threshold", 0.5)  # 50% drop

    async def detect_regime_shock(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect and respond to black swan events (regime shocks)."""
        try:
            alerts = []
            for _, row in market_data.iterrows():
                symbol = row.get("symbol", "BTC/USD")
                volatility = float(row.get("volatility", 0.0))
                liquidity = float(row.get("liquidity_score", 1.0))
                historical_vol = float(row.get("historical_volatility", 1.0))

                volatility_z_score = (volatility - historical_vol) / historical_vol if historical_vol else 0.0
                liquidity_ratio = liquidity / row.get("historical_liquidity", 1.0)

                if volatility_z_score > self.volatility_spike_threshold or liquidity_ratio < self.liquidity_drop_threshold:
                    alert = {
                        "type": "black_swan_alert",
                        "symbol": symbol,
                        "volatility_z_score": volatility_z_score,
                        "liquidity_ratio": liquidity_ratio,
                        "timestamp": int(time.time()),
                        "description": f"Black swan detected for {symbol}: Volatility z-score {volatility_z_score:.2f}, Liquidity ratio {liquidity_ratio:.2f}"
                    }
                    alerts.append(alert)
                    self.logger.log_issue(alert)
                    self.cache.store_incident(alert)
                    self.redis_client.set(f"risk_management:black_swan:{symbol}", str(alert), ex=3600)
                    await self.notify_execution(alert)

            summary = {
                "type": "black_swan_summary",
                "alert_count": len(alerts),
                "timestamp": int(time.time()),
                "description": f"Detected {len(alerts)} black swan events"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return alerts
        except Exception as e:
            self.logger.log(f"Error detecting black swan: {e}")
            self.cache.store_incident({
                "type": "black_swan_guard_error",
                "timestamp": int(time.time()),
                "description": f"Error detecting black swan: {str(e)}"
            })
            return []

    async def notify_execution(self, alert: Dict[str, Any]):
        """Notify Executions Agent to pause or adjust trades."""
        self.logger.log(f"Notifying Executions Agent: {alert.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(alert))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of black swan detection."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))