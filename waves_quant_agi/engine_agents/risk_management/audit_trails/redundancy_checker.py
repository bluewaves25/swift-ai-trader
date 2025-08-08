from typing import Dict, Any, List
import time
import redis
import pandas as pd
from ..logs.risk_management_logger import RiskManagementLogger

class RedundancyChecker:
    def __init__(self, config: Dict[str, Any], logger: RiskManagementLogger):
        self.config = config
        self.logger = logger
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.correlation_threshold = config.get("correlation_threshold", 0.9)  # 90% correlation for redundancy

    async def check_redundancy(self, risk_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect redundant risk checks for efficiency."""
        try:
            redundancies = []
            risk_types = risk_data["type"].unique()
            for i, type1 in enumerate(risk_types):
                for type2 in risk_types[i+1:]:
                    data1 = risk_data[risk_data["type"] == type1][["symbol", "risk_score"]]
                    data2 = risk_data[risk_data["type"] == type2][["symbol", "risk_score"]]
                    merged = data1.merge(data2, on="symbol", how="inner")
                    if not merged.empty:
                        correlation = merged["risk_score_x"].corr(merged["risk_score_y"])
                        if correlation > self.correlation_threshold:
                            redundancy = {
                                "type": "redundancy_check",
                                "risk_type_1": type1,
                                "risk_type_2": type2,
                                "correlation": correlation,
                                "timestamp": int(time.time()),
                                "description": f"Redundant risk checks detected: {type1} and {type2} (Correlation {correlation:.2f})"
                            }
                            redundancies.append(redundancy)
                            self.logger.log_risk_assessment("assessment", redundancy)
                            self.redis_client.set(f"risk_management:redundancy:{type1}:{type2}", str(redundancy), ex=604800)

            summary = {
                "type": "redundancy_check_summary",
                "redundancy_count": len(redundancies),
                "timestamp": int(time.time()),
                "description": f"Detected {len(redundancies)} redundant risk checks"
            }
            self.logger.log_risk_assessment("black_swan_summary", summary)
            await self.notify_core(summary)
            return redundancies
        except Exception as e:
            self.logger.log_error(f"Error: {e}")
            return []

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of redundancy check results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("risk_management_output", str(issue))