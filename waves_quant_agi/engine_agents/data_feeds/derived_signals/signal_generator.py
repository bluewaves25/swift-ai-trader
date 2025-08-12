from typing import Dict, Any, Optional
from ..utils.data_cleaner import DataCleaner
from ..utils.timestamp_utils import TimestampUtils
from ..utils.schema_validator import SchemaValidator
from ..stream.realtime_publisher import RealtimePublisher
from ..cache.db_connector import DBConnector

class SignalGenerator:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.cleaner = DataCleaner()
        self.timestamp_utils = TimestampUtils()
        self.validator = SchemaValidator()
        self.publisher = RealtimePublisher()
        self.db = DBConnector()
        self.schema = {
            "symbol": str,
            "signal_type": str,  # e.g., "buy", "sell", "hold"
            "strength": float,  # 0 to 1
            "timestamp": float
        }

    def generate_signal(self, indicators: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate trading signal based on indicators."""
        try:
            symbol = indicators.get("symbol")
            rsi = next((i["value"] for i in indicators.get("indicators", []) if i["indicator"] == "rsi"), 0.0)
            vwap = next((i["value"] for i in indicators.get("indicators", []) if i["indicator"] == "vwap"), 0.0)
            current_price = indicators.get("price", 0.0)
            
            # Simple signal logic: RSI-based
            signal_type = "hold"
            strength = 0.5
            if rsi > 70 and current_price > vwap:
                signal_type = "sell"
                strength = (rsi - 70) / 30
            elif rsi < 30 and current_price < vwap:
                signal_type = "buy"
                strength = (30 - rsi) / 30
            
            signal = {
                "symbol": symbol,
                "signal_type": signal_type,
                "strength": min(max(strength, 0.0), 1.0),
                "timestamp": self.timestamp_utils.get_timestamp()
            }
            
            if self.validator.validate(signal, self.schema):
                cleaned_signal = self.cleaner.clean(signal)
                return cleaned_signal
            return None
        except Exception as e:
            print(f"Error generating signal for {symbol}: {e}")
            return None

    def process_and_publish(self, indicators: Dict[str, Any]):
        """Process and publish generated signal."""
        signal = self.generate_signal(indicators)
        if signal:
            self.publisher.publish("trading_signal", signal)
            self.db.store(signal)