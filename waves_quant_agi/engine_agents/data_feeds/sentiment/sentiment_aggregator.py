from typing import Dict, Any, List, Optional
import asyncio
from ..utils.data_cleaner import DataCleaner
from ..utils.timestamp_utils import TimestampUtils
from ..utils.schema_validator import SchemaValidator
from ..stream.realtime_publisher import RealtimePublisher
from ..cache.db_connector import DBConnector

class SentimentAggregator:
    def __init__(self, interval: int = 300):
        self.interval = interval  # seconds
        self.cleaner = DataCleaner()
        self.timestamp_utils = TimestampUtils()
        self.validator = SchemaValidator()
        self.publisher = RealtimePublisher()
        self.db = DBConnector()
        self.sentiment_data = []
        self.schema = {
            "keyword": str,
            "aggregate_sentiment": float,
            "sources": list,
            "timestamp": float
        }

    def aggregate(self, data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Aggregate sentiment data from multiple sources."""
        try:
            if not data:
                return None
            keywords = {d["keyword"] for d in data}
            for keyword in keywords:
                relevant_data = [d for d in data if d["keyword"] == keyword]
                if not relevant_data:
                    continue
                sentiment_sum = sum(d["sentiment"] for d in relevant_data)
                avg_sentiment = sentiment_sum / len(relevant_data)
                sources = [d["source"] for d in relevant_data]
                aggregated = {
                    "keyword": keyword,
                    "aggregate_sentiment": avg_sentiment,
                    "sources": sources,
                    "timestamp": self.timestamp_utils.get_timestamp()
                }
                if self.validator.validate(aggregated, self.schema):
                    cleaned_data = self.cleaner.clean(aggregated)
                    return cleaned_data
            return None
        except Exception as e:
            print(f"Error aggregating sentiment: {e}")
            return None

    async def stream_aggregated_sentiment(self):
        """Stream aggregated sentiment data."""
        while True:
            aggregated = self.aggregate(self.sentiment_data)
            if aggregated:
                self.publisher.publish("aggregated_sentiment", aggregated)
                self.db.store(aggregated)
            self.sentiment_data.clear()  # Reset after aggregation
            await asyncio.sleep(self.interval)

    def add_sentiment_data(self, data: Dict[str, Any]):
        """Add sentiment data for aggregation."""
        self.sentiment_data.append(data)