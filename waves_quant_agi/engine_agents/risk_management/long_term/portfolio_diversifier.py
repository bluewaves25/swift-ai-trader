from typing import Dict, Any, List
import pandas as pd
import numpy as np
import time

class PortfolioDiversifier:
    def __init__(self, connection_manager, config: Dict[str, Any]):
        self.config = config
        self.connection_manager = connection_manager
        self.correlation_threshold = config.get("correlation_threshold", 0.3)  # Max correlation for diversification

    async def assess_diversification(self, portfolio_data: pd.DataFrame) -> float:
        """Assess portfolio diversification across uncorrelated assets."""
        try:
        symbols = portfolio_data.get("symbol", []).unique()
            if len(symbols) < 2:
                
                return 0.0

            # Calculate correlation matrix (placeholder)
            returns = portfolio_data.pivot(columns="symbol", values="returns").fillna(0)
            correlation_matrix = np.corrcoef(returns.values.T)
            max_correlation = np.max(np.abs(correlation_matrix - np.eye(len(symbols))))

            diversification_score = 1.0 - max_correlation
            if max_correlation > self.correlation_threshold:
                issue = {
                    "type": "diversification_issue",
                    "symbols": list(symbols),
                    "max_correlation": float(max_correlation),
                    "timestamp": int(time.time()),
                    "description": f"High correlation detected: {max_correlation:.2f}"
                }
                self.logger.log_risk_alert("diversification_issue", issue)
                redis_client = await self.connection_manager.get_redis_client()
                        if redis_client:
                            redis_client.set("risk_management:diversification", str(issue), ex=604800)

            summary = {
                "type": "diversification_summary",
                "score": diversification_score,
                "timestamp": int(time.time()),
                "description": f"Portfolio diversification score: {diversification_score:.2f}"
            }
            self.logger.log_risk_assessment("diversification_summary", summary)
            await self.notify_core(summary)
            return diversification_score
        except Exception as e:
        print(f"Error in {os.path.basename(file_path)}: {e}")
            return 0.0

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of diversification results."""
        }")
        redis_client = await self.connection_manager.get_redis_client()
        if redis_client:
        redis_client.publish("risk_management_output", str(issue))