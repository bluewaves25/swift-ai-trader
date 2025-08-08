import asyncio
import requests
from typing import Dict, Any, Optional
from ..utils.data_cleaner import DataCleaner
from ..utils.timestamp_utils import TimestampUtils
from ..utils.schema_validator import SchemaValidator
from ..stream.realtime_publisher import RealtimePublisher
from ..cache.db_connector import DBConnector

class NewsScraper:
    def __init__(self, api_key: str, sources: list, keywords: list, interval: int = 300):
        self.api_key = api_key
        self.sources = sources  # e.g., ["newsapi.org"]
        self.keywords = keywords  # e.g., ["Bitcoin", "market"]
        self.interval = interval  # seconds
        self.cleaner = DataCleaner()
        self.timestamp_utils = TimestampUtils()
        self.validator = SchemaValidator()
        self.publisher = RealtimePublisher()
        self.db = DBConnector()
        self.schema = {
            "source": str,
            "keyword": str,
            "sentiment": float,  # Placeholder: -1 to 1
            "title": str,
            "timestamp": float
        }

    async def fetch_news(self, source: str, keyword: str) -> Optional[Dict[str, Any]]:
        """Fetch news articles for a keyword from a source."""
        try:
            url = f"https://newsapi.org/v2/everything?q={keyword}&sources={source}&apiKey={self.api_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            articles = response.json().get("articles", [])
            if not articles:
                return None
            # Placeholder: Use first article for simplicity, implement sentiment analysis (e.g., VADER)
            article = articles[0]
            data = {
                "source": source,
                "keyword": keyword,
                "sentiment": 0.0,  # Placeholder
                "title": article.get("title", "")[:500],  # Truncate for storage
                "timestamp": self.timestamp_utils.get_timestamp()
            }
            if self.validator.validate(data, self.schema):
                cleaned_data = self.cleaner.clean(data)
                return cleaned_data
            return None
        except Exception as e:
            print(f"Error fetching news for {keyword} from {source}: {e}")
            return None

    async def stream_news(self):
        """Stream news sentiment data for all keywords and sources."""
        while True:
            tasks = [self.fetch_news(source, keyword) for source in self.sources for keyword in self.keywords]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for data in results:
                if data:
                    self.publisher.publish("news_sentiment", data)
                    self.db.store(data)
            await asyncio.sleep(self.interval)