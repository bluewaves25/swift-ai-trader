from typing import Dict, Any
from collections import defaultdict
import time
from ..logs.broker_logger import BrokerLogger

class PerformanceTracker:
    def __init__(self):
        self.logger = BrokerLogger("performance_tracker")
        self.metrics = defaultdict(lambda: {'avg_latency': 0.0, 'error_count': 0, 'success_count': 0, 'fee': 0.0})

    def record_response(self, broker_name: str, latency: float, success: bool, fee: float = 0.0):
        """Record broker response metrics."""
        metrics = self.metrics[broker_name]
        metrics['avg_latency'] = (metrics['avg_latency'] * metrics['success_count'] + latency) / (metrics['success_count'] + 1)
        metrics['success_count'] += 1 if success else 0
        metrics['error_count'] += 0 if success else 1
        metrics['fee'] = fee if fee > 0 else metrics['fee']
        self.logger.log_request("performance", {"broker": broker_name, "metrics": dict(metrics)})

    def get_broker_metrics(self) -> Dict[str, Any]:
        """Return current metrics for all brokers."""
        return dict(self.metrics)

    def reset_metrics(self, broker_name: str = None):
        """Reset metrics for a specific broker or all brokers."""
        if broker_name:
            self.metrics[broker_name] = {'avg_latency': 0.0, 'error_count': 0, 'success_count': 0, 'fee': 0.0}
        else:
            self.metrics.clear()
        self.logger.log_request("reset_metrics", {"broker": broker_name or "all"})