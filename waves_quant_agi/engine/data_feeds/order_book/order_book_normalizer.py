from typing import Dict, Any, Optional
from ..utils.data_cleaner import DataCleaner
from ..utils.timestamp_utils import TimestampUtils
from ..utils.schema_validator import SchemaValidator
from ..stream.realtime_publisher import RealtimePublisher
from ..cache.db_connector import DBConnector

class OrderBookNormalizer:
    def __init__(self):
        self.cleaner = DataCleaner()
        self.timestamp_utils = TimestampUtils()
        self.validator = SchemaValidator()
        self.publisher = RealtimePublisher()
        self.db = DBConnector()
        self.schema = {
            "exchange": str,
            "symbol": str,
            "bids": list,  # [[price, amount], ...]
            "asks": list,  # [[price, amount], ...]
            "timestamp": float
        }

    def normalize(self, order_book: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize order book data to a standard format."""
        try:
            if not self.validator.validate(order_book, self.schema):
                print(f"Invalid order book data: {order_book}")
                return None
            
            normalized = {
                "exchange": str(order_book["exchange"]).lower(),
                "symbol": str(order_book["symbol"]).replace("/", ""),
                "bids": [[float(price), float(amount)] for price, amount in order_book["bids"]],
                "asks": [[float(price), float(amount)] for price, amount in order_book["asks"]],
                "timestamp": float(order_book["timestamp"])
            }
            cleaned_data = self.cleaner.clean(normalized)
            return cleaned_data
        except Exception as e:
            print(f"Error normalizing order book: {e}")
            return None

    def process_and_publish(self, order_book: Dict[str, Any]):
        """Process and publish normalized order book data."""
        normalized_data = self.normalize(order_book)
        if normalized_data:
            self.publisher.publish("normalized_order_book", normalized_data)
            self.db.store(normalized_data)