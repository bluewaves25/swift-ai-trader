from typing import Dict, Any, Optional
from ..utils.data_cleaner import DataCleaner
from ..utils.timestamp_utils import TimestampUtils
from ..utils.schema_validator import SchemaValidator
from ..stream.realtime_publisher import RealtimePublisher
from ..cache.db_connector import DBConnector

class TradeParser:
    def __init__(self):
        self.cleaner = DataCleaner()
        self.timestamp_utils = TimestampUtils()
        self.validator = SchemaValidator()
        self.publisher = RealtimePublisher()
        self.db = DBConnector()
        self.schema = {
            "exchange": str,
            "symbol": str,
            "price": float,
            "amount": float,
            "side": str,  # "buy" or "sell"
            "timestamp": float
        }

    def parse_trade(self, trade: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse and normalize trade tape data."""
        try:
            if not self.validator.validate(trade, self.schema):
                print(f"Invalid trade data: {trade}")
                return None
            
            parsed = {
                "exchange": str(trade["exchange"]).lower(),
                "symbol": str(trade["symbol"]).replace("/", ""),
                "price": float(trade["price"]),
                "amount": float(trade["amount"]),
                "side": str(trade["side"]).lower(),
                "timestamp": float(trade["timestamp"])
            }
            cleaned_data = self.cleaner.clean(parsed)
            return cleaned_data
        except Exception as e:
            print(f"Error parsing trade: {e}")
            return None

    def process_and_publish(self, trade: Dict[str, Any]):
        """Process and publish parsed trade tape data."""
        parsed_data = self.parse_trade(trade)
        if parsed_data:
            self.publisher.publish("parsed_trade_tape", parsed_data)
            self.db.store(parsed_data)