from typing import Dict, Any
from .pattern_analyzer import PatternAnalyzer
from ..logs.broker_logger import BrokerLogger

class BrokerIntelligence:
    def __init__(self, pattern_analyzer: PatternAnalyzer):
        self.analyzer = pattern_analyzer
        self.logger = BrokerLogger("broker_intelligence")
        self.recommendations = {}

    def update_recommendations(self, broker_name: str, metrics: Dict[str, Any]):
        """Generate recommendations based on metrics and patterns."""
        analysis = self.analyzer.analyze_patterns(broker_name)
        recommendation = {
            'broker': broker_name,
            'disable': False,
            'priority': 1.0
        }

        if analysis['total_failures'] > 10 or metrics.get('error_count', 0) > 5:
            recommendation['disable'] = True
        elif metrics.get('avg_latency', 0) > 1.0:
            recommendation['priority'] = 0.5

        self.recommendations[broker_name] = recommendation
        self.logger.log_request("recommendation", recommendation)

    def get_recommendations(self, broker_name: str) -> Dict[str, Any]:
        """Get recommendations for a broker."""
        return self.recommendations.get(broker_name, {'broker': broker_name, 'disable': False, 'priority': 1.0})