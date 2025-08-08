from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ..logs.risk_management_logger import RiskManagementLogger

class MacroExposureManager:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.macro_risk_threshold = config.get("macro_risk_threshold", 0.6)  # Macro risk score

    async def track_macro_alignment(self, macro_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Track portfolio alignment with macro themes."""
        try:
            alignments = []
            for _, row in macro_data.iterrows():
                symbol = row.get("symbol", "USD/JPY")
                macro_score = float(row.get("macro_score", 0.0))  # Score from macro indicators

                if macro_score > self.macro_risk_threshold:
                    alignment = {
                        "type": "macro_alignment",
                        "symbol": symbol,
                        "macro_score": macro_score,
                        "timestamp": int(time.time()),
                        "description": f"High macro risk for {symbol}: Score {macro_score:.2f}"
                    }
                    alignments.append(alignment)
                    self.logger.log_risk_assessment("macro_alignment", alignment)
                    self.redis_client.set(f"risk_management:macro:{symbol}", str(alignment), ex=3600)
                    await self.notify_execution(alignment)

            summary = {
                "type": "macro_alignment_summary",
                "alignment_count": len(alignments),
                "timestamp": int(time.time()),
                "description": f"Tracked {len(alignments)} macro alignments"
            }
            self.logger.log_risk_assessment("macro_alignment_summary", summary)
            await self.notify_core(summary)
            return alignments
        except Exception as e:
            self.logger.log_error(f"Error tracking macro alignment: {e}")
            return []

    async def notify_execution(self, alignment: Dict[str, Any]):
        """Notify Executions Agent of macro risk adjustments."""
        self.logger.log(f"Notifying Executions Agent: {alignment.get('description', 'unknown')}")
        self.redis_client.publish("execution_agent", str(alignment))

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of macro alignment results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))