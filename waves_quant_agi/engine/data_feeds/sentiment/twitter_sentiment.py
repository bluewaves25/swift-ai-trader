import asyncio
from typing import Dict, Any, Optional
import tweepy
from ..utils.data_cleaner import DataCleaner
from ..utils.timestamp_utils import TimestampUtils
from ..utils.schema_validator import SchemaValidator
from ..stream.realtime_publisher import RealtimePublisher
from ..cache.db_connector import DBConnector

class TwitterSentiment:
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str, keywords: list, interval: int = 60):
        self.auth = tweepy.OAuthHandler(api_key, api_secret)
        self.auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)
        self.keywords = keywords  # e.g., ["BTC", "Bitcoin", "#crypto"]
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
            "text": str,
            "timestamp": float
        }

    async def fetch_sentiment(self, keyword: str) -> Optional[Dict[str, Any]]:
        """Fetch sentiment for a keyword from Twitter."""
        try:
            tweets = self.api.search_tweets(q=keyword, lang="en", count=100, tweet_mode="extended")
            sentiment_score = 0.0  # Placeholder: Implement actual sentiment analysis (e.g., VADER)
            text = " ".join(tweet.full_text for tweet in tweets)
            data = {
                "source": "twitter",
                "keyword": keyword,
                "sentiment": sentiment_score,
                "text": text[:500],  # Truncate for storage
                "timestamp": self.timestamp_utils.get_timestamp()
            }
            if self.validator.validate(data, self.schema):
                cleaned_data = self.cleaner.clean(data)
                return cleaned_data
            return None
        except Exception as e:
            print(f"Error fetching sentiment for {keyword}: {e}")
            return None

    async def stream_sentiment(self):
        """Stream sentiment data for all keywords."""
        while True:
            tasks = [self.fetch_sentiment(keyword) for keyword in self.keywords]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for data in results:
                if data:
                    self.publisher.publish("twitter_sentiment", data)
                    self.db.store(data)
            
            await asyncio.sleep(self.interval)