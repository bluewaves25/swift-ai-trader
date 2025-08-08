from typing import Dict, Any, List
import numpy as np
from ..utils.data_cleaner import DataCleaner
from ..utils.timestamp_utils import TimestampUtils
from ..utils.schema_validator import SchemaValidator
from ..stream.realtime_publisher import RealtimePublisher
from ..cache.db_connector import DBConnector

class Indicators:
    def __init__(self, window: int = 14):
        self.window = window  # Window for calculations (e.g., RSI, SMA)
        self.cleaner = DataCleaner()
        self.timestamp_utils = TimestampUtils()
        self.validator = SchemaValidator()
        self.publisher = RealtimePublisher()
        self.db = DBConnector()
        self.schema = {
            "symbol": str,
            "indicator": str,
            "value": float,
            "timestamp": float
        }

    def calculate_rsi(self, prices: List[float]) -> float:
        """Calculate Relative Strength Index (RSI)."""
        if len(prices) < self.window:
            return 0.0
        prices = np.array(prices)
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-self.window:])
        avg_loss = np.mean(losses[-self.window:])
        rs = avg_gain / avg_loss if avg_loss != 0 else 0.0
        return 100 - (100 / (1 + rs))

    def calculate_vwap(self, prices: List[float], volumes: List[float]) -> float:
        """Calculate Volume Weighted Average Price (VWAP)."""
        if len(prices) < 1 or len(volumes) < 1:
            return 0.0
        prices, volumes = np.array(prices), np.array(volumes)
        return np.sum(prices * volumes) / np.sum(volumes) if np.sum(volumes) != 0 else 0.0

    def process_indicators(self, data: Dict[str, Any], price_history: Dict[str, List[float]], volume_history: Dict[str, List[float]]):
        """Calculate and publish indicators for given data."""
        try:
            symbol = data["symbol"]
            price = data["price"]
            volume = data["volume"]
            
            # Update histories
            price_history[symbol] = price_history.get(symbol, [])[-self.window + 1:] + [price]
            volume_history[symbol] = volume_history.get(symbol, [])[-self.window + 1:] + [volume]
            
            # Calculate indicators
            indicators = [
                {"symbol": symbol, "indicator": "rsi", "value": self.calculate_rsi(price_history[symbol]), "timestamp": data["timestamp"]},
                {"symbol": symbol, "indicator": "vwap", "value": self.calculate_vwap(price_history[symbol], volume_history[symbol]), "timestamp": data["timestamp"]}
            ]
            
            for indicator in indicators:
                if self.validator.validate(indicator, self.schema):
                    cleaned_indicator = self.cleaner.clean(indicator)
                    self.publisher.publish("indicator", cleaned_indicator)
                    self.db.store(cleaned_indicator)
        except Exception as e:
            print(f"Error calculating indicators for {symbol}: {e}")