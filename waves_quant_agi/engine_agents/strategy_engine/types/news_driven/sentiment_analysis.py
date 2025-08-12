#!/usr/bin/env python3
"""
Sentiment Analysis Strategy - Fixed and Enhanced
News-driven trading using sentiment analysis.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
import numpy as np
from engine_agents.shared_utils import get_shared_redis

class SentimentAnalysisStrategy:
    """Sentiment analysis strategy for news-driven trading."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        
        # Strategy parameters
        self.sentiment_threshold = config.get("sentiment_threshold", 0.6)  # 60% sentiment threshold
        self.confidence_threshold = config.get("confidence_threshold", 0.7)  # 70% confidence threshold
        self.news_impact_duration = config.get("news_impact_duration", 3600)  # 1 hour impact
        self.min_volume_spike = config.get("min_volume_spike", 2.0)  # 2x volume spike
        self.sentiment_decay_rate = config.get("sentiment_decay_rate", 0.1)  # 10% decay per hour
        
        # Sentiment sources
        self.sentiment_sources = ["news", "social_media", "earnings_calls", "fed_speeches"]

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect sentiment-based trading opportunities."""
        try:
            opportunities = []
            
            if not market_data:
                return opportunities
            
            for data in market_data:
                symbol = data.get("symbol", "")
                if not symbol:
                    continue
                
                opportunity = await self._check_sentiment_opportunity(symbol, data)
                if opportunity:
                    opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting sentiment opportunities: {e}")
            return []

    async def _check_sentiment_opportunity(self, symbol: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for sentiment-based opportunity in a specific symbol."""
        try:
            close_price = float(data.get("close", 0.0))
            volume = float(data.get("volume", 0.0))
            
            if close_price <= 0:
                return None
            
            # Get sentiment data
            sentiment_data = await self._get_sentiment_data(symbol)
            if not sentiment_data:
                return None
            
            # Calculate sentiment metrics
            sentiment_metrics = await self._calculate_sentiment_metrics(
                symbol, sentiment_data, volume
            )
            
            if not sentiment_metrics['opportunity_detected']:
                return None
            
            # Determine trade direction
            if sentiment_metrics['sentiment_score'] > self.sentiment_threshold:
                action = "buy"  # Positive sentiment
                entry_price = close_price
                stop_loss = close_price * (1 - sentiment_metrics['stop_loss'])
                take_profit = close_price * (1 + sentiment_metrics['take_profit'])
            else:
                action = "sell"  # Negative sentiment
                entry_price = close_price
                stop_loss = close_price * (1 + sentiment_metrics['stop_loss'])
                take_profit = close_price * (1 - sentiment_metrics['take_profit'])
            
            opportunity = {
                "type": "sentiment_analysis",
                "strategy": "news_driven",
                "symbol": symbol,
                "action": action,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "confidence": sentiment_metrics['confidence'],
                "sentiment_score": sentiment_metrics['sentiment_score'],
                "sentiment_confidence": sentiment_metrics['sentiment_confidence'],
                "news_impact": sentiment_metrics['news_impact'],
                "volume_spike": sentiment_metrics['volume_spike'],
                "impact_duration": self.news_impact_duration,
                "timestamp": int(time.time()),
                "description": f"Sentiment opportunity for {symbol}: Score {sentiment_metrics['sentiment_score']:.3f}, Action {action}"
            }
            
            # Store in Redis
            if self.redis_conn:
                try:
                    import json
                    self.redis_conn.set(
                        f"strategy_engine:sentiment:{symbol}:{int(time.time())}", 
                        json.dumps(opportunity), 
                        ex=3600
                    )
                except json.JSONEncodeError as e:
                    if self.logger:
                        self.logger.error(f"JSON encoding error storing sentiment opportunity: {e}")
                except ConnectionError as e:
                    if self.logger:
                        self.logger.error(f"Redis connection error storing sentiment opportunity: {e}")
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Unexpected error storing sentiment opportunity: {e}")
            
            if self.logger:
                self.logger.info(f"Sentiment analysis opportunity: {opportunity['description']}")
            
            return opportunity
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking sentiment opportunity: {e}")
            return None

    async def _get_sentiment_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get sentiment data for a symbol."""
        try:
            if not self.redis_conn:
                return None
            
            # Get sentiment from multiple sources
            sentiment_data = {}
            
            for source in self.sentiment_sources:
                source_key = f"sentiment:{source}:{symbol}"
                source_data = self.redis_conn.get(source_key)
                
                if source_data:
                    import json
                    try:
                        sentiment_data[source] = json.loads(source_data)
                    except:
                        continue
            
            return sentiment_data if sentiment_data else None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting sentiment data: {e}")
            return None

    async def _calculate_sentiment_metrics(self, symbol: str, sentiment_data: Dict[str, Any], 
                                        volume: float) -> Dict[str, Any]:
        """Calculate sentiment metrics and detect opportunities."""
        try:
            # Calculate composite sentiment score
            sentiment_scores = []
            confidence_scores = []
            
            for source, data in sentiment_data.items():
                if isinstance(data, dict):
                    score = data.get("sentiment_score", 0.5)
                    confidence = data.get("confidence", 0.5)
                    timestamp = data.get("timestamp", 0)
                    
                    # Apply time decay
                    if timestamp > 0:
                        time_diff = time.time() - timestamp
                        decay_factor = 1.0 / (1.0 + self.sentiment_decay_rate * time_diff / 3600)
                        score = 0.5 + (score - 0.5) * decay_factor
                    
                    sentiment_scores.append(score)
                    confidence_scores.append(confidence)
            
            if not sentiment_scores:
                return {
                    "opportunity_detected": False,
                    "sentiment_score": 0.5,
                    "sentiment_confidence": 0.0,
                    "news_impact": 0.0,
                    "volume_spike": 1.0,
                    "stop_loss": 0.02,
                    "take_profit": 0.03
                }
            
            # Calculate weighted average sentiment
            composite_sentiment = np.average(sentiment_scores, weights=confidence_scores)
            composite_confidence = np.mean(confidence_scores)
            
            # Get volume spike
            volume_spike = await self._calculate_volume_spike(symbol, volume)
            
            # Calculate news impact
            news_impact = await self._calculate_news_impact(sentiment_data)
            
            # Determine if opportunity exists
            sentiment_threshold_met = abs(composite_sentiment - 0.5) > (self.sentiment_threshold - 0.5)
            confidence_threshold_met = composite_confidence > self.confidence_threshold
            volume_threshold_met = volume_spike > self.min_volume_spike
            
            opportunity_detected = (sentiment_threshold_met and 
                                 confidence_threshold_met and 
                                 volume_threshold_met)
            
            # Calculate position sizing parameters
            sentiment_strength = abs(composite_sentiment - 0.5) * 2  # 0 to 1
            stop_loss = 0.02 + (1 - sentiment_strength) * 0.03  # 2% to 5%
            take_profit = 0.03 + sentiment_strength * 0.04  # 3% to 7%
            
            return {
                "opportunity_detected": opportunity_detected,
                "sentiment_score": composite_sentiment,
                "sentiment_confidence": composite_confidence,
                "news_impact": news_impact,
                "volume_spike": volume_spike,
                "stop_loss": stop_loss,
                "take_profit": take_profit
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating sentiment metrics: {e}")
            return {
                "opportunity_detected": False,
                "sentiment_score": 0.5,
                "sentiment_confidence": 0.0,
                "news_impact": 0.0,
                "volume_spike": 1.0,
                "stop_loss": 0.02,
                "take_profit": 0.03
            }

    async def _calculate_volume_spike(self, symbol: str, current_volume: float) -> float:
        """Calculate volume spike relative to historical average."""
        try:
            if not self.redis_conn:
                return 1.0
            
            # Get historical volume data
            volume_key = f"volume_history:{symbol}"
            volume_history = self.redis_conn.get(volume_key)
            
            if volume_history:
                import json
                try:
                    volumes = json.loads(volume_history)
                    if volumes and len(volumes) > 0:
                        avg_volume = np.mean(volumes)
                        if avg_volume > 0:
                            return current_volume / avg_volume
                except:
                    pass
            
            return 1.0
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating volume spike: {e}")
            return 1.0

    async def _calculate_news_impact(self, sentiment_data: Dict[str, Any]) -> float:
        """Calculate overall news impact score."""
        try:
            impact_scores = []
            
            for source, data in sentiment_data.items():
                if isinstance(data, dict):
                    impact = data.get("impact_score", 0.5)
                    timestamp = data.get("timestamp", 0)
                    
                    # Apply time decay
                    if timestamp > 0:
                        time_diff = time.time() - timestamp
                        decay_factor = 1.0 / (1.0 + self.sentiment_decay_rate * time_diff / 3600)
                        impact = 0.5 + (impact - 0.5) * decay_factor
                    
                    impact_scores.append(impact)
            
            if impact_scores:
                return np.mean(impact_scores)
            
            return 0.5
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating news impact: {e}")
            return 0.5

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Sentiment Analysis Strategy",
            "type": "news_driven",
            "description": "News-driven trading using sentiment analysis",
            "parameters": {
                "sentiment_threshold": self.sentiment_threshold,
                "confidence_threshold": self.confidence_threshold,
                "news_impact_duration": self.news_impact_duration,
                "min_volume_spike": self.min_volume_spike,
                "sentiment_decay_rate": self.sentiment_decay_rate
            },
            "timeframe": "tactical",  # 30s tier
            "asset_types": ["crypto", "forex", "stocks"],
            "execution_speed": "medium"
        }