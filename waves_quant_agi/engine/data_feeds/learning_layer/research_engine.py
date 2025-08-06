from typing import Dict, Any, List
from ..cache.db_connector import DBConnector

class ResearchEngine:
    def __init__(self, db: DBConnector):
        self.db = db

    def analyze_feed_behavior(self, key_pattern: str = "*") -> Dict[str, Any]:
        """Analyze data feed behavior from stored data."""
        try:
            data_points = self.db.backfill(key_pattern)
            if not data_points:
                return {"status": "no_data"}
            
            analysis = {
                "total_records": len(data_points),
                "symbols": set(d["symbol"] for d in data_points if "symbol" in d),
                "types": set(d.get("type", "generic") for d in data_points),
                "timestamp_range": {
                    "min": min(float(d["timestamp"]) for d in data_points if "timestamp" in d),
                    "max": max(float(d["timestamp"]) for d in data_points if "timestamp" in d)
                }
            }
            
            # Analyze specific metrics (e.g., price volatility)
            prices = [float(d["price"]) for d in data_points if "price" in d]
            if prices:
                analysis["price_volatility"] = max(prices) - min(prices)
            
            return analysis
        except Exception as e:
            print(f"Error analyzing feed behavior: {e}")
            return {"status": "error", "error": str(e)}

    def collect_training_data(self, key_pattern: str = "*") -> List[Dict[str, Any]]:
        """Collect data for training from Redis."""
        try:
            return self.db.backfill(key_pattern)
        except Exception as e:
            print(f"Error collecting training data: {e}")
            return []