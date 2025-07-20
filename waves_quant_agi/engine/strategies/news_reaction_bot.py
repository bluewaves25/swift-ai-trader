from transformers import pipeline
from waves_quant_agi.engine.strategies.base_strategy import BaseStrategy

class NewsReactionBot(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.sentiment_pipeline = pipeline("sentiment-analysis")

    def analyze(self, news_text):
        sentiment = self.sentiment_pipeline(news_text[:512])[0]
        label = sentiment['label']
        if label == "POSITIVE":
            return "buy"
        elif label == "NEGATIVE":
            return "sell"
        return "hold"
