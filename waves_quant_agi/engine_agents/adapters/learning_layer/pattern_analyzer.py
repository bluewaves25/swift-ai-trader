from typing import Dict, Any, List
from collections import defaultdict
import time
from ..logs.broker_logger import BrokerLogger

class PatternAnalyzer:
    def __init__(self):
        self.logger = BrokerLogger("pattern_analyzer")
        self.failure_patterns = defaultdict(list)

    def log_failure(self, broker_name: str, error: str, order: Dict[str, Any]):
        """Log a failure event for analysis."""
        timestamp = time.time()
        self.failure_patterns[broker_name].append({
            'error': error,
            'order': order,
            'timestamp': timestamp
        })
        self.logger.log_request("failure", {"broker": broker_name, "error": error})

    def analyze_patterns(self, broker_name: str) -> Dict[str, Any]:
        """Analyze failure patterns for a broker."""
        patterns = self.failure_patterns[broker_name]
        error_counts = defaultdict(int)
        time_patterns = defaultdict(int)

        for event in patterns:
            error_counts[event['error']] += 1
            hour = time.localtime(event['timestamp']).tm_hour
            time_patterns[hour] += 1

        common_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_hours = sorted(time_patterns.items(), key=lambda x: x[1], reverse=True)[:3]

        analysis = {
            'common_errors': common_errors,
            'peak_failure_hours': peak_hours,
            'total_failures': len(patterns)
        }
        self.logger.log_request("analysis", {"broker": broker_name, "analysis": analysis})
        return analysis

    def clear_patterns(self, broker_name: str = None):
        """Clear failure patterns for a broker or all brokers."""
        if broker_name:
            self.failure_patterns[broker_name].clear()
        else:
            self.failure_patterns.clear()
        self.logger.log_request("clear_patterns", {"broker": broker_name or "all"})