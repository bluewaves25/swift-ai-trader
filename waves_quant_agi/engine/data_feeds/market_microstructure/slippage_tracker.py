from typing import Dict, Any, Optional
from ..utils.data_cleaner import DataCleaner
from ..utils.timestamp_utils import TimestampUtils
from ..utils.schema_validator import SchemaValidator
from ..stream.realtime_publisher import RealtimePublisher
from ..cache.db_connector import DBConnector

class SlippageTracker:
    def __init__(self):
        self.cleaner = DataCleaner()
        self.timestamp_utils = TimestampUtils()
        self.validator = SchemaValidator()
        self.publisher = RealtimePublisher()
        self.db = DBConnector()
        self.schema = {
            "symbol": str,
            "slippage": float,  # Price difference between expected and actual execution
            "order_size": float,
            "timestamp": float
        }

    def calculate_slippage(self, trade: Dict[str, Any], order_book: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calculate slippage based on trade and order book data."""
        try:
            symbol = trade["symbol"]
            executed_price = trade["price"]
            order_size = trade["amount"]
            best_ask = order_book["asks"][0][0] if trade["side"] == "buy" else order_book["bids"][0][0]
            slippage = abs(executed_price - best_ask) / best_ask if best_ask != 0 else 0.0
            
            data = {
                "symbol": symbol,
                "slippage": slippage,
                "order_size": order_size,
                "timestamp": self.timestamp_utils.get_timestamp()
            }
            
            if self.validator.validate(data, self.schema):
                cleaned_data = self.cleaner.clean(data)
                return cleaned_data
            return None
        except Exception as e:
            print(f"Error calculating slippage for {symbol}: {e}")
            return None

    def process_and_publish(self, trade: Dict[str, Any], order_book: Dict[str, Any]):
        """Process and publish slippage metrics."""
        slippage_data = self.calculate_slippage(trade, order_book)
        if slippage_data:
            self.publisher.publish("slippage", slippage_data)
            self.db.store(slippage_data)