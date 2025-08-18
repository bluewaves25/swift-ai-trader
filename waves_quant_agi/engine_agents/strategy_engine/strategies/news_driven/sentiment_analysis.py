#!/usr/bin/env python3
"""
Sentiment Analysis Strategy - News Driven
Focuses purely on strategy-specific tasks, delegating risk management to the risk management agent.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
import numpy as np
from datetime import datetime

# Import consolidated trading components (updated paths for new structure)
from ...core.memory.trading_context import TradingContext
from ...core.learning.trading_research_engine import TradingResearchEngine


class SentimentAnalysisStrategy:
    """Sentiment analysis strategy for news-driven trading."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext()
        self.trading_research_engine = TradingResearchEngine()
        
        # Strategy parameters
        self.sentiment_threshold = config.get("sentiment_threshold", 0.6)  # 0.6 sentiment score
        self.news_impact_threshold = config.get("news_impact_threshold", 0.05)  # 5% price impact
        self.volume_confirmation = config.get("volume_confirmation", 1.5)  # 1.5x average volume
        self.lookback_period = config.get("lookback_period", 50)  # 50 periods
        
        # Strategy state
        self.last_signal_time = None
        self.strategy_performance = {"total_signals": 0, "average_confidence": 0.0}

    async def initialize(self) -> bool:
        """Initialize the strategy and trading components."""
        try:
            await self.trading_context.initialize()
            await self.trading_research_engine.initialize()
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize sentiment analysis strategy: {e}")
            return False

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect sentiment analysis opportunities."""
        if not market_data or len(market_data) < self.lookback_period:
            return []
        
        try:
            # Convert to DataFrame for analysis
            df = pd.DataFrame(market_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').tail(self.lookback_period)
            
            opportunities = []
            
            for _, row in df.iterrows():
                symbol = row.get("symbol", "BTCUSD")
                current_price = float(row.get("close", 0.0))
                current_volume = float(row.get("volume", 0.0))
                sentiment_score = float(row.get("sentiment_score", 0.0))
                news_impact = float(row.get("news_impact", 0.0))
                
                # Calculate sentiment metrics
                sentiment_metrics = await self._calculate_sentiment_metrics(
                    current_price, current_volume, sentiment_score, news_impact, market_data
                )
                
                # Check if sentiment signal meets criteria
                if self._is_valid_sentiment_signal(sentiment_metrics):
                    signal = self._generate_sentiment_signal(
                        symbol, current_price, sentiment_metrics
                    )
                    if signal:
                        self.trading_context.store_signal(signal)
                        opportunities.append(signal)
                        
                        # Update strategy performance
                        self.strategy_performance["total_signals"] += 1
                        self.strategy_performance["average_confidence"] = (
                            (self.strategy_performance["average_confidence"] * 
                             (self.strategy_performance["total_signals"] - 1) + signal["confidence"]) /
                            self.strategy_performance["total_signals"]
                        )
                        
                        self.last_signal_time = datetime.now()
                        
                        if self.logger:
                            self.logger.info(f"Sentiment signal generated: {signal['signal_type']} for {symbol}")
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting sentiment analysis opportunities: {e}")
            return []

    async def _calculate_sentiment_metrics(self, current_price: float, current_volume: float, 
                                         sentiment_score: float, news_impact: float, 
                                         market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate sentiment metrics for analysis."""
        try:
            # Calculate volume metrics
            volumes = [float(d.get("volume", 0)) for d in market_data if d.get("volume")]
            avg_volume = np.mean(volumes) if volumes else current_volume
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Calculate sentiment strength
            sentiment_strength = abs(sentiment_score - 0.5) * 2  # Convert to 0-1 scale
            
            # Calculate news impact strength
            news_impact_strength = abs(news_impact) / self.news_impact_threshold if self.news_impact_threshold > 0 else 0
            
            # Calculate price momentum
            prices = [float(d.get("close", 0)) for d in market_data if d.get("close")]
            if len(prices) > 1:
                price_momentum = (current_price - prices[0]) / prices[0] if prices[0] > 0 else 0
            else:
                price_momentum = 0.0
            
            # Calculate sentiment consistency
            sentiment_scores = [float(d.get("sentiment_score", 0.5)) for d in market_data if d.get("sentiment_score")]
            if len(sentiment_scores) > 1:
                sentiment_consistency = 1.0 - np.std(sentiment_scores)  # Higher consistency = lower std
            else:
                sentiment_consistency = 0.5
            
            return {
                "sentiment_score": sentiment_score,
                "sentiment_strength": sentiment_strength,
                "news_impact": news_impact,
                "news_impact_strength": news_impact_strength,
                "volume_ratio": volume_ratio,
                "price_momentum": price_momentum,
                "sentiment_consistency": sentiment_consistency,
                "current_price": current_price,
                "current_volume": current_volume
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating sentiment metrics: {e}")
            return {}

    def _is_valid_sentiment_signal(self, metrics: Dict[str, Any]) -> bool:
        """Check if sentiment signal meets criteria."""
        try:
            if not metrics:
                return False
            
            sentiment_strength = metrics.get("sentiment_strength", 0.0)
            news_impact_strength = metrics.get("news_impact_strength", 0.0)
            volume_ratio = metrics.get("volume_ratio", 1.0)
            sentiment_consistency = metrics.get("sentiment_consistency", 0.5)
            
            # Check sentiment strength
            if sentiment_strength < self.sentiment_threshold:
                return False
            
            # Check news impact
            if news_impact_strength < 1.0:
                return False
            
            # Check volume confirmation
            if volume_ratio < self.volume_confirmation:
                return False
            
            # Check sentiment consistency
            if sentiment_consistency < 0.3:
                return False
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error validating sentiment signal: {e}")
            return False

    def _generate_sentiment_signal(self, symbol: str, current_price: float, 
                                  metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate sentiment trading signal."""
        try:
            sentiment_score = metrics.get("sentiment_score", 0.5)
            sentiment_strength = metrics.get("sentiment_strength", 0.0)
            news_impact_strength = metrics.get("news_impact_strength", 0.0)
            volume_ratio = metrics.get("volume_ratio", 1.0)
            price_momentum = metrics.get("price_momentum", 0.0)
            
            # Determine signal type
            if sentiment_score > 0.5:
                signal_type = "SENTIMENT_BULLISH"
                confidence = min(sentiment_strength, 1.0)
            else:
                signal_type = "SENTIMENT_BEARISH"
                confidence = min(sentiment_strength, 1.0)
            
            # Adjust confidence based on other factors
            news_confidence = min(news_impact_strength, 1.0)
            volume_confidence = min(volume_ratio / self.volume_confirmation, 1.0)
            momentum_confidence = min(abs(price_momentum) / self.news_impact_threshold, 1.0)
            
            final_confidence = (confidence + news_confidence + volume_confidence + momentum_confidence) / 4
            
            signal = {
                "signal_id": f"sentiment_{int(time.time())}",
                "strategy_id": "sentiment_analysis",
                "strategy_type": "news_driven",
                "signal_type": signal_type,
                "symbol": symbol,
                "timestamp": datetime.now().isoformat(),
                "price": current_price,
                "confidence": final_confidence,
                "metadata": {
                    "sentiment_score": sentiment_score,
                    "sentiment_strength": sentiment_strength,
                    "news_impact": metrics.get("news_impact", 0.0),
                    "news_impact_strength": news_impact_strength,
                    "volume_ratio": volume_ratio,
                    "price_momentum": price_momentum
                }
            }
            
            return signal
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error generating sentiment signal: {e}")
            return None

    async def cleanup(self):
        """Cleanup strategy resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error during strategy cleanup: {e}")