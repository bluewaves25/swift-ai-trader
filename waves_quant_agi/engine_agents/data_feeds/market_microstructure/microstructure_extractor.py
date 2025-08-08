from typing import Dict, Any, Optional
from ..utils.data_cleaner import DataCleaner
from ..utils.timestamp_utils import TimestampUtils
from ..utils.schema_validator import SchemaValidator
from ..stream.realtime_publisher import RealtimePublisher
from ..cache.db_connector import DBConnector

class MicrostructureExtractor:
    def __init__(self):
        self.cleaner = DataCleaner()
        self.timestamp_utils = TimestampUtils()
        self.validator = SchemaValidator()
        self.publisher = RealtimePublisher()
        self.db = DBConnector()
        self.schema = {
            "symbol": str,
            "spread": float,
            "liquidity": float,
            "timestamp": float
        }

    def extract_metrics(self, order_book: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract market microstructure metrics from order book."""
        try:
            bids = order_book.get("bids", [])
            asks = order_book.get("asks", [])
            if not bids or not asks:
                return None
            
            # Calculate spread
            best_bid = bids[0][0]
            best_ask = asks[0][0]
            spread = best_ask - best_bid
            
            # Calculate liquidity (sum of bid/ask volumes at top level)
            bid_volume = sum(amount for _, amount in bids[:5])
            ask_volume = sum(amount for _, amount in asks[:5])
            liquidity = bid_volume + ask_volume
            
            metrics = {
                "symbol": order_book["symbol"],
                "spread": spread,
                "liquidity": liquidity,
                "timestamp": order_book["timestamp"]
            }
            
            if self.validator.validate(metrics, self.schema):
                cleaned_metrics = self.cleaner.clean(metrics)
                return cleaned_metrics
            return None
        except Exception as e:
            print(f"Error extracting microstructure for {order_book.get('symbol', 'unknown')}: {e}")
            return None

    def process_and_publish(self, order_book: Dict[str, Any]):
        """Process and publish microstructure metrics."""
        metrics = self.extract_metrics(order_book)
        if metrics:
            self.publisher.publish("microstructure", metrics)
            self.db.store(metrics)