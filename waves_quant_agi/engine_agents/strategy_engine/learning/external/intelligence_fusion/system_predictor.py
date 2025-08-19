#!/usr/bin/env python3
"""
System Predictor
Integrates external intelligence for comprehensive market prediction.
"""

import asyncio
import time
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from ........shared_utils import get_shared_logger, get_shared_redis

class SystemPredictor:
    """Integrates external intelligence for market prediction."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "system_predictor")
        self.redis_conn = get_shared_redis()
        
        # Prediction configuration
        self.prediction_horizon = config.get("prediction_horizon", 24)  # hours
        self.confidence_threshold = config.get("confidence_threshold", 0.7)
        self.update_frequency = config.get("update_frequency", 300)  # 5 minutes
        
        # Intelligence sources
        self.intelligence_sources = [
            "news_sentiment",
            "social_media",
            "economic_indicators",
            "technical_analysis",
            "fundamental_analysis",
            "market_microstructure"
        ]
        
        # Prediction state
        self.current_predictions: Dict[str, Dict[str, Any]] = {}
        self.prediction_history: List[Dict[str, Any]] = []
        self.intelligence_cache: Dict[str, Dict[str, Any]] = {}
        
        # Prediction statistics
        self.stats = {
            "predictions_generated": 0,
            "predictions_accurate": 0,
            "intelligence_sources_used": 0,
            "prediction_errors": 0,
            "start_time": time.time()
        }

    async def start_prediction_system(self):
        """Start the prediction system."""
        try:
            self.logger.info("🚀 Starting System Predictor...")
            
            # Start background prediction loop
            asyncio.create_task(self._prediction_loop())
            
            # Start intelligence gathering
            asyncio.create_task(self._intelligence_gathering_loop())
            
            self.logger.info("✅ System Predictor started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error starting prediction system: {e}")

    async def _prediction_loop(self):
        """Main prediction generation loop."""
        while True:
            try:
                # Generate predictions
                await self._generate_predictions()
                
                # Update prediction accuracy
                await self._update_prediction_accuracy()
                
                # Wait for next cycle
                await asyncio.sleep(self.update_frequency)
                
            except Exception as e:
                self.logger.error(f"Error in prediction loop: {e}")
                await asyncio.sleep(60)

    async def _intelligence_gathering_loop(self):
        """Gather intelligence from various sources."""
        while True:
            try:
                # Gather intelligence from all sources
                for source in self.intelligence_sources:
                    await self._gather_intelligence(source)
                
                # Wait for next cycle
                await asyncio.sleep(self.update_frequency)
                
            except Exception as e:
                self.logger.error(f"Error in intelligence gathering loop: {e}")
                await asyncio.sleep(60)

    async def _gather_intelligence(self, source: str):
        """Gather intelligence from a specific source."""
        try:
            if source == "news_sentiment":
                await self._gather_news_sentiment()
            elif source == "social_media":
                await self._gather_social_media()
            elif source == "economic_indicators":
                await self._gather_economic_indicators()
            elif source == "technical_analysis":
                await self._gather_technical_analysis()
            elif source == "fundamental_analysis":
                await self._gather_fundamental_analysis()
            elif source == "market_microstructure":
                await self._gather_market_microstructure()
                
        except Exception as e:
            self.logger.error(f"Error gathering intelligence from {source}: {e}")

    async def _gather_news_sentiment(self):
        """Gather news sentiment intelligence."""
        try:
            # Get news sentiment from Redis
            sentiment_key = "news_feeds:sentiment:latest"
            sentiment_data = self.redis_conn.get(sentiment_key)
            
            if sentiment_data:
                import json
                sentiment = json.loads(sentiment_data)
                
                # Store in intelligence cache
                self.intelligence_cache["news_sentiment"] = {
                    "data": sentiment,
                    "timestamp": time.time(),
                    "source": "news_feeds"
                }
                
        except Exception as e:
            self.logger.error(f"Error gathering news sentiment: {e}")

    async def _gather_social_media(self):
        """Gather social media intelligence."""
        try:
            # Get social media sentiment from Redis
            social_key = "social_media:sentiment:latest"
            social_data = self.redis_conn.get(social_key)
            
            if social_data:
                import json
                social = json.loads(social_data)
                
                # Store in intelligence cache
                self.intelligence_cache["social_media"] = {
                    "data": social,
                    "timestamp": time.time(),
                    "source": "social_media"
                }
                
        except Exception as e:
            self.logger.error(f"Error gathering social media: {e}")

    async def _gather_economic_indicators(self):
        """Gather economic indicators intelligence."""
        try:
            # Get economic indicators from Redis
            indicators_key = "data_feeds:economic_indicators"
            indicators_data = self.redis_conn.get(indicators_key)
            
            if indicators_data:
                import json
                indicators = json.loads(indicators_data)
                
                # Store in intelligence cache
                self.intelligence_cache["economic_indicators"] = {
                    "data": indicators,
                    "timestamp": time.time(),
                    "source": "data_feeds"
                }
                
        except Exception as e:
            self.logger.error(f"Error gathering economic indicators: {e}")

    async def _gather_technical_analysis(self):
        """Gather technical analysis intelligence."""
        try:
            # Get technical analysis from Redis
            technical_key = "market_data:technical_analysis"
            technical_data = self.redis_conn.get(technical_key)
            
            if technical_data:
                import json
                technical = json.loads(technical_data)
                
                # Store in intelligence cache
                self.intelligence_cache["technical_analysis"] = {
                    "data": technical,
                    "timestamp": time.time(),
                    "source": "market_data"
                }
                
        except Exception as e:
            self.logger.error(f"Error gathering technical analysis: {e}")

    async def _gather_fundamental_analysis(self):
        """Gather fundamental analysis intelligence."""
        try:
            # Get fundamental analysis from Redis
            fundamental_key = "data_feeds:fundamental_analysis"
            fundamental_data = self.redis_conn.get(fundamental_key)
            
            if fundamental_data:
                import json
                fundamental = json.loads(fundamental_data)
                
                # Store in intelligence cache
                self.intelligence_cache["fundamental_analysis"] = {
                    "data": fundamental,
                    "timestamp": time.time(),
                    "source": "data_feeds"
                }
                
        except Exception as e:
            self.logger.error(f"Error gathering fundamental analysis: {e}")

    async def _gather_market_microstructure(self):
        """Gather market microstructure intelligence."""
        try:
            # Get market microstructure from Redis
            microstructure_key = "market_data:microstructure"
            microstructure_data = self.redis_conn.get(microstructure_key)
            
            if microstructure_data:
                import json
                microstructure = json.loads(microstructure_data)
                
                # Store in intelligence cache
                self.intelligence_cache["market_microstructure"] = {
                    "data": microstructure,
                    "timestamp": time.time(),
                    "source": "market_data"
                }
                
        except Exception as e:
            self.logger.error(f"Error gathering market microstructure: {e}")

    async def _generate_predictions(self):
        """Generate comprehensive market predictions."""
        try:
            # Get available symbols
            symbols = await self._get_available_symbols()
            
            for symbol in symbols:
                # Generate prediction for each symbol
                prediction = await self._generate_symbol_prediction(symbol)
                
                if prediction:
                    # Store prediction
                    self.current_predictions[symbol] = prediction
                    
                    # Add to history
                    self.prediction_history.append(prediction)
                    
                    # Limit history size
                    if len(self.prediction_history) > 1000:
                        self.prediction_history = self.prediction_history[-1000:]
                    
                    # Update statistics
                    self.stats["predictions_generated"] += 1
                    
                    # Store in Redis
                    await self._store_prediction(symbol, prediction)
                    
        except Exception as e:
            self.logger.error(f"Error generating predictions: {e}")

    async def _generate_symbol_prediction(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Generate prediction for a specific symbol."""
        try:
            # Get intelligence data
            intelligence_data = await self._get_intelligence_data()
            
            # Generate prediction components
            price_prediction = await self._predict_price_movement(symbol, intelligence_data)
            volatility_prediction = await self._predict_volatility(symbol, intelligence_data)
            trend_prediction = await self._predict_trend(symbol, intelligence_data)
            
            # Calculate overall confidence
            confidence = self._calculate_prediction_confidence(
                price_prediction, volatility_prediction, trend_prediction
            )
            
            # Only return predictions above confidence threshold
            if confidence >= self.confidence_threshold:
                prediction = {
                    "symbol": symbol,
                    "timestamp": int(time.time()),
                    "prediction_horizon": self.prediction_horizon,
                    "price_prediction": price_prediction,
                    "volatility_prediction": volatility_prediction,
                    "trend_prediction": trend_prediction,
                    "confidence": confidence,
                    "intelligence_sources": list(self.intelligence_cache.keys()),
                    "prediction_type": "comprehensive"
                }
                
                return prediction
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating prediction for {symbol}: {e}")
            return None

    async def _predict_price_movement(self, symbol: str, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict price movement for a symbol."""
        try:
            # Get current market data
            market_data = await self._get_symbol_market_data(symbol)
            
            if not market_data:
                return {"direction": "neutral", "magnitude": 0.0, "confidence": 0.0}
            
            # Analyze intelligence data for price impact
            price_impact = self._analyze_price_impact(intelligence_data, market_data)
            
            # Generate prediction
            prediction = {
                "direction": price_impact["direction"],
                "magnitude": price_impact["magnitude"],
                "confidence": price_impact["confidence"],
                "factors": price_impact["factors"]
            }
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting price movement: {e}")
            return {"direction": "neutral", "magnitude": 0.0, "confidence": 0.0}

    async def _predict_volatility(self, symbol: str, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict volatility for a symbol."""
        try:
            # Get current volatility data
            volatility_data = await self._get_symbol_volatility_data(symbol)
            
            if not volatility_data:
                return {"level": "normal", "change": 0.0, "confidence": 0.0}
            
            # Analyze intelligence data for volatility impact
            volatility_impact = self._analyze_volatility_impact(intelligence_data, volatility_data)
            
            # Generate prediction
            prediction = {
                "level": volatility_impact["level"],
                "change": volatility_impact["change"],
                "confidence": volatility_impact["confidence"],
                "factors": volatility_impact["factors"]
            }
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting volatility: {e}")
            return {"level": "normal", "change": 0.0, "confidence": 0.0}

    async def _predict_trend(self, symbol: str, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict trend for a symbol."""
        try:
            # Get current trend data
            trend_data = await self._get_symbol_trend_data(symbol)
            
            if not trend_data:
                return {"direction": "neutral", "strength": 0.0, "confidence": 0.0}
            
            # Analyze intelligence data for trend impact
            trend_impact = self._analyze_trend_impact(intelligence_data, trend_data)
            
            # Generate prediction
            prediction = {
                "direction": trend_impact["direction"],
                "strength": trend_impact["strength"],
                "confidence": trend_impact["confidence"],
                "factors": trend_impact["factors"]
            }
            
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting trend: {e}")
            return {"direction": "neutral", "strength": 0.0, "confidence": 0.0}

    def _analyze_price_impact(self, intelligence_data: Dict[str, Any], market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze intelligence data for price impact."""
        try:
            # Simple analysis - can be enhanced with ML models
            impact_score = 0.0
            factors = []
            
            # News sentiment impact
            if "news_sentiment" in intelligence_data:
                sentiment = intelligence_data["news_sentiment"]["data"]
                if sentiment.get("overall_sentiment", 0) > 0.6:
                    impact_score += 0.3
                    factors.append("positive_news")
                elif sentiment.get("overall_sentiment", 0) < 0.4:
                    impact_score -= 0.3
                    factors.append("negative_news")
            
            # Economic indicators impact
            if "economic_indicators" in intelligence_data:
                indicators = intelligence_data["economic_indicators"]["data"]
                if indicators.get("gdp_growth", 0) > 0.02:
                    impact_score += 0.2
                    factors.append("strong_gdp")
                elif indicators.get("inflation", 0) > 0.03:
                    impact_score -= 0.2
                    factors.append("high_inflation")
            
            # Determine direction and magnitude
            if impact_score > 0.2:
                direction = "up"
                magnitude = min(1.0, impact_score)
            elif impact_score < -0.2:
                direction = "down"
                magnitude = min(1.0, abs(impact_score))
            else:
                direction = "neutral"
                magnitude = 0.0
            
            confidence = min(1.0, abs(impact_score) + 0.3)
            
            return {
                "direction": direction,
                "magnitude": magnitude,
                "confidence": confidence,
                "factors": factors
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing price impact: {e}")
            return {"direction": "neutral", "magnitude": 0.0, "confidence": 0.0, "factors": []}

    def _analyze_volatility_impact(self, intelligence_data: Dict[str, Any], volatility_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze intelligence data for volatility impact."""
        try:
            # Simple analysis - can be enhanced with ML models
            impact_score = 0.0
            factors = []
            
            # News sentiment volatility impact
            if "news_sentiment" in intelligence_data:
                sentiment = intelligence_data["news_sentiment"]["data"]
                if sentiment.get("sentiment_volatility", 0) > 0.7:
                    impact_score += 0.4
                    factors.append("high_news_volatility")
            
            # Economic indicators volatility impact
            if "economic_indicators" in intelligence_data:
                indicators = intelligence_data["economic_indicators"]["data"]
                if indicators.get("policy_uncertainty", 0) > 0.6:
                    impact_score += 0.3
                    factors.append("policy_uncertainty")
            
            # Determine level and change
            if impact_score > 0.3:
                level = "high"
                change = min(1.0, impact_score)
            elif impact_score < -0.3:
                level = "low"
                change = max(-1.0, impact_score)
            else:
                level = "normal"
                change = 0.0
            
            confidence = min(1.0, abs(impact_score) + 0.4)
            
            return {
                "level": level,
                "change": change,
                "confidence": confidence,
                "factors": factors
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing volatility impact: {e}")
            return {"level": "normal", "change": 0.0, "confidence": 0.0, "factors": []}

    def _analyze_trend_impact(self, intelligence_data: Dict[str, Any], trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze intelligence data for trend impact."""
        try:
            # Simple analysis - can be enhanced with ML models
            impact_score = 0.0
            factors = []
            
            # Technical analysis impact
            if "technical_analysis" in intelligence_data:
                technical = intelligence_data["technical_analysis"]["data"]
                if technical.get("trend_strength", 0) > 0.7:
                    impact_score += 0.3
                    factors.append("strong_technical_trend")
            
            # Fundamental analysis impact
            if "fundamental_analysis" in intelligence_data:
                fundamental = intelligence_data["fundamental_analysis"]["data"]
                if fundamental.get("earnings_growth", 0) > 0.1:
                    impact_score += 0.2
                    factors.append("strong_earnings")
            
            # Determine direction and strength
            if impact_score > 0.2:
                direction = "up"
                strength = min(1.0, impact_score)
            elif impact_score < -0.2:
                direction = "down"
                strength = min(1.0, abs(impact_score))
            else:
                direction = "neutral"
                strength = 0.0
            
            confidence = min(1.0, abs(impact_score) + 0.3)
            
            return {
                "direction": direction,
                "strength": strength,
                "confidence": confidence,
                "factors": factors
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing trend impact: {e}")
            return {"direction": "neutral", "strength": 0.0, "confidence": 0.0, "factors": []}

    def _calculate_prediction_confidence(self, price_prediction: Dict[str, Any], 
                                       volatility_prediction: Dict[str, Any], 
                                       trend_prediction: Dict[str, Any]) -> float:
        """Calculate overall prediction confidence."""
        try:
            # Weighted average of individual confidences
            confidence = (
                price_prediction.get("confidence", 0.0) * 0.4 +
                volatility_prediction.get("confidence", 0.0) * 0.3 +
                trend_prediction.get("confidence", 0.0) * 0.3
            )
            
            return confidence
            
        except Exception as e:
            self.logger.error(f"Error calculating prediction confidence: {e}")
            return 0.0

    async def _get_available_symbols(self) -> List[str]:
        """Get available symbols from Redis."""
        try:
            # Get symbols from Redis
            symbols_key = "data_feeds:available_symbols"
            symbols_data = self.redis_conn.get(symbols_key)
            
            if symbols_data:
                import json
                symbols = json.loads(symbols_data)
                return symbols[:20]  # Limit to top 20 symbols
            
            return ["BTCUSDm", "ETHUSDm", "XRPUSDm"]  # Fallback
            
        except Exception as e:
            self.logger.error(f"Error getting available symbols: {e}")
            return ["BTCUSDm", "ETHUSDm", "XRPUSDm"]

    async def _get_intelligence_data(self) -> Dict[str, Any]:
        """Get current intelligence data."""
        return self.intelligence_cache.copy()

    async def _get_symbol_market_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get market data for a specific symbol."""
        try:
            # Get market data from Redis
            market_key = f"market_data:{symbol}"
            market_data = self.redis_conn.hgetall(market_key)
            
            if market_data:
                return market_data
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting market data for {symbol}: {e}")
            return None

    async def _get_symbol_volatility_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get volatility data for a specific symbol."""
        try:
            # Get volatility data from Redis
            volatility_key = f"market_data:volatility:{symbol}"
            volatility_data = self.redis_conn.get(volatility_key)
            
            if volatility_data:
                import json
                return json.loads(volatility_data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting volatility data for {symbol}: {e}")
            return None

    async def _get_symbol_trend_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get trend data for a specific symbol."""
        try:
            # Get trend data from Redis
            trend_key = f"market_data:trend:{symbol}"
            trend_data = self.redis_conn.get(trend_key)
            
            if trend_data:
                import json
                return json.loads(trend_data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting trend data for {symbol}: {e}")
            return None

    async def _store_prediction(self, symbol: str, prediction: Dict[str, Any]):
        """Store prediction in Redis."""
        try:
            # Store prediction
            prediction_key = f"strategy_engine:predictions:{symbol}"
            self.redis_conn.set(prediction_key, str(prediction), ex=3600)  # 1 hour
            
            # Publish prediction update
            self.redis_conn.publish("strategy_engine:prediction_updates", str(prediction))
            
        except Exception as e:
            self.logger.error(f"Error storing prediction: {e}")

    async def _update_prediction_accuracy(self):
        """Update prediction accuracy based on actual outcomes."""
        try:
            # This would compare predictions with actual outcomes
            # For now, just log the process
            self.logger.info("Updating prediction accuracy...")
            
        except Exception as e:
            self.logger.error(f"Error updating prediction accuracy: {e}")

    async def get_predictions(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Get current predictions."""
        try:
            if symbol:
                return self.current_predictions.get(symbol, {})
            else:
                return self.current_predictions.copy()
                
        except Exception as e:
            self.logger.error(f"Error getting predictions: {e}")
            return {}

    async def get_prediction_stats(self) -> Dict[str, Any]:
        """Get prediction statistics."""
        return {
            **self.stats,
            "current_predictions_count": len(self.current_predictions),
            "prediction_history_size": len(self.prediction_history),
            "intelligence_sources_count": len(self.intelligence_cache),
            "uptime": time.time() - self.stats["start_time"]
        }

    async def force_prediction_update(self, symbol: str):
        """Force a prediction update for a specific symbol."""
        try:
            self.logger.info(f"Forcing prediction update for {symbol}")
            
            # Generate new prediction
            prediction = await self._generate_symbol_prediction(symbol)
            
            if prediction:
                # Update current prediction
                self.current_predictions[symbol] = prediction
                
                # Store in Redis
                await self._store_prediction(symbol, prediction)
                
                self.logger.info(f"Prediction updated for {symbol}")
            else:
                self.logger.warning(f"Could not generate prediction for {symbol}")
                
        except Exception as e:
            self.logger.error(f"Error forcing prediction update: {e}")

    async def stop_prediction_system(self):
        """Stop the prediction system."""
        try:
            self.logger.info("🛑 Stopping System Predictor...")
            
            # Store final predictions
            for symbol, prediction in self.current_predictions.items():
                await self._store_prediction(symbol, prediction)
            
            self.logger.info("✅ System Predictor stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping prediction system: {e}")