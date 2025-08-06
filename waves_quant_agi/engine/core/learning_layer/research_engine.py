from typing import Dict, Any, List
from ..memory.recent_context import RecentContext
from ..logs.core_agent_logger import CoreAgentLogger

class ResearchEngine:
    def __init__(self, context: RecentContext):
        self.context = context
        self.logger = CoreAgentLogger("research_engine")

    def analyze_behavior(self) -> Dict[str, Any]:
        """Analyze agent behavior based on recent context."""
        rejections = self.context.get_recent_rejections()
        signals = self.context.get_recent_signals()
        
        rejection_counts = {}
        for rejection in rejections:
            reason = rejection["reason"]
            rejection_counts[reason] = rejection_counts.get(reason, 0) + 1
        
        signal_counts = {}
        for signal in signals:
            strategy = signal.get("strategy", "unknown")
            signal_counts[strategy] = signal_counts.get(strategy, 0) + 1
        
        analysis = {
            "rejection_summary": rejection_counts,
            "signal_summary": signal_counts,
            "total_signals": len(signals),
            "total_rejections": len(rejections)
        }
        self.logger.log_action("analyze_behavior", analysis)
        return analysis

    def collect_market_data(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect and process market data for training."""
        try:
            processed_data = {
                "market": external_data.get("market", {}),
                "timestamp": external_data.get("timestamp"),
                "metrics": external_data.get("metrics", {})
            }
            self.logger.log_action("collect_market_data", {"data": processed_data})
            return processed_data
        except Exception as e:
            self.logger.log_action("collect_market_data", {"error": str(e)})
            return {}