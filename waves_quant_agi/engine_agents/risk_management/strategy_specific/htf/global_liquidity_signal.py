from typing import Dict, Any, List
import time
import pandas as pd

class GlobalLiquiditySignalRisk:
    def __init__(self, connection_manager, config: Dict[str, Any]):
        self.config = config
        self.connection_manager = connection_manager
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
                fee_score = float(redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.get(f"fee_monitor:{symbol}:fee_score") or 0.0)

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
                
                decision)
                redis_client = await self.connection_manager.get_redis_client()
                        if redis_client:
                            redis_client.set(f"risk_management:global_liquidity:{symbol}", str(decision), ex=3600)
                if decision["description"].startswith("Global liquidity approved"):
                    await self.notify_execution(decision)

            summary = {
                "type": "global_liquidity_summary",
                "decision_count": len(risk_decisions),
                "timestamp": int(time.time()),
                "description": f"Evaluated {len(risk_decisions)} global liquidity risks"
            }
            
            await self.notify_core(summary)
            return risk_decisions
        except Exception as e:
            print(f"Error in {os.path.basename(file_path)}: {e}")
            return []

    async def notify_execution(self, decision: Dict[str, Any]):
        """Notify Executions Agent of approved global liquidity risk."""
        }")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("execution_agent", str(decision))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of global liquidity risk evaluation results."""
        }")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
            redis_client.publish("risk_management_output", str(issue))