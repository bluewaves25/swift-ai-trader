from typing import Dict, Any, List
import time
import pandas as pd
import numpy as np

class BlackSwanGuard:
    def __init__(self, connection_manager, config: Dict[str, Any]):
        self.config = config
        self.connection_manager = connection_manager
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
                    # Store alert in Redis using connection manager
                    redis_client = await self.connection_manager.get_redis_client()
                    if redis_client:
                        redis_client.set(f"risk_management:black_swan:{symbol}", str(alert), ex=3600)
                        await self.notify_execution(alert)

            summary = {
                "type": "black_swan_summary",
                "alert_count": len(alerts),
                "timestamp": int(time.time()),
                "description": f"Detected {len(alerts)} black swan events"
            }
            await self.notify_core(summary)
            return alerts
        except Exception as e:
            print(f"Error detecting black swan: {e}")
            return []

    async def notify_execution(self, alert: Dict[str, Any]):
        """Notify Executions Agent to pause or adjust trades."""
        print(f"Notifying Executions Agent: {alert.get('description', 'unknown')}")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("execution_agent", str(alert))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of black swan detection."""
        print(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("risk_management_output", str(issue))