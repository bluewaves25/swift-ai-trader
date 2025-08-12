#!/usr/bin/env python3
"""
ML Composer - Fixed and Enhanced
Generates ML-based strategy blueprints using machine learning models.
"""

from typing import Dict, Any, List, Optional
import time
import numpy as np
import asyncio
from engine_agents.shared_utils import get_shared_redis, get_shared_logger

class MLComposer:
    """ML-based strategy composer using machine learning models."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "ml_composer")
        self.redis_conn = get_shared_redis()
        
        # ML model configuration
        self.confidence_threshold = config.get("confidence_threshold", 0.7)
        self.min_data_points = config.get("min_data_points", 50)
        self.model_update_frequency = config.get("model_update_frequency", 3600)  # 1 hour
        
        # Strategy composition state
        self.composed_strategies: Dict[str, Dict[str, Any]] = {}
        self.model_performance: Dict[str, float] = {}
        
        # ML model state (placeholder for actual model)
        self.model_ready = False
        self.last_model_update = 0
        
        self.stats = {
            "strategies_composed": 0,
            "high_confidence_strategies": 0,
            "model_predictions": 0,
            "model_errors": 0,
            "start_time": time.time()
        }

    async def initialize_model(self) -> bool:
        """Initialize the ML model."""
        try:
            # Check if we have enough data
            training_data = await self._get_training_data()
            
            if len(training_data) < self.min_data_points:
                self.logger.warning(f"Insufficient training data: {len(training_data)} < {self.min_data_points}")
                return False
            
            # Initialize model (placeholder for actual ML model)
            self.model_ready = True
            self.last_model_update = time.time()
            
            self.logger.info("ML model initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing ML model: {e}")
            return False

    async def compose_strategy(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate ML-based strategy blueprints based on market conditions."""
        try:
            if not self.model_ready:
                if not await self.initialize_model():
                    self.logger.warning("ML model not ready, skipping strategy composition")
                    return []
            
            # Check if model needs updating
            if time.time() - self.last_model_update > self.model_update_frequency:
                await self._update_model()
            
            strategies = []
            
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                strategy_type = data.get("type", "unknown")
                
                # Extract features for ML model
                features = await self._extract_features(data)
                if features is None:
                    continue
                
                # Generate ML prediction
                prediction = await self._generate_prediction(features)
                if prediction is None:
                    continue
                
                self.stats["model_predictions"] += 1
                
                # Check confidence threshold
                if prediction["confidence"] > self.confidence_threshold:
                    strategy = await self._create_ml_strategy(symbol, strategy_type, prediction, data)
                    if strategy:
                        strategies.append(strategy)
                        
                        # Store composed strategy
                        await self._store_composed_strategy(strategy)
                        
                        self.stats["strategies_composed"] += 1
                        if prediction["confidence"] > 0.8:
                            self.stats["high_confidence_strategies"] += 1

            self.logger.info(f"Composed {len(strategies)} ML-based strategies")
            return strategies
            
        except Exception as e:
            self.logger.error(f"Error composing ML strategies: {e}")
            self.stats["model_errors"] += 1
            return []

    async def _get_training_data(self) -> List[Dict[str, Any]]:
        """Get training data for the ML model."""
        try:
            # Get historical strategy performance data
            training_key = "strategy_engine:training_data"
            training_data = self.redis_conn.get(training_key)
            
            if training_data:
                import json
                try:
                    # Handle both string and bytes responses from Redis
                    if isinstance(training_data, bytes):
                        training_data = training_data.decode('utf-8')
                    elif not isinstance(training_data, str):
                        self.logger.warning(f"Invalid training data type: {type(training_data)}")
                        return []
                        
                    parsed_data = json.loads(training_data)
                    if isinstance(parsed_data, list):
                        return parsed_data
                    else:
                        self.logger.warning(f"Invalid training data format: expected list, got {type(parsed_data)}")
                        return []
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for training data: {e}")
                    return []
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing training data: {e}")
                    return []
            
            # Fallback: get from performance history
            performance_data = []
            try:
                for key in self.redis_conn.scan_iter("strategy_engine:performance_history:*"):
                    try:
                        data = self.redis_conn.get(key)
                        if data:
                            # Handle both string and bytes responses from Redis
                            if isinstance(data, bytes):
                                data = data.decode('utf-8')
                            elif not isinstance(data, str):
                                continue
                                
                            parsed_data = json.loads(data)
                            if isinstance(parsed_data, list):
                                performance_data.extend(parsed_data)
                            elif isinstance(parsed_data, dict):
                                performance_data.append(parsed_data)
                    except (json.JSONDecodeError, Exception) as e:
                        self.logger.warning(f"Error parsing performance data from key {key}: {e}")
                        continue
                        
            except Exception as e:
                self.logger.error(f"Error scanning performance history: {e}")
            
            return performance_data
            
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting training data: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error getting training data: {e}")
            return []

    async def _extract_features(self, market_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """Extract features for ML model."""
        try:
            # Extract relevant features
            features = []
            
            # Price-based features
            close_price = float(market_data.get("close", 0.0))
            if close_price <= 0:
                return None
            
            # Volatility features
            volatility = float(market_data.get("volatility", 0.0))
            features.append(volatility)
            
            # Trend features
            trend_score = float(market_data.get("trend_score", 0.0))
            features.append(trend_score)
            
            # Volume features
            volume = float(market_data.get("volume", 0.0))
            avg_volume = float(market_data.get("avg_volume", volume))
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1.0
            features.append(volume_ratio)
            
            # Technical indicators
            rsi = float(market_data.get("rsi", 50.0)) / 100.0  # Normalize to 0-1
            features.append(rsi)
            
            macd = float(market_data.get("macd", 0.0))
            features.append(macd)
            
            # Market regime features
            market_regime = market_data.get("market_regime", "normal")
            regime_encoding = {"normal": 0.0, "volatile": 0.5, "trending": 1.0}.get(market_regime, 0.0)
            features.append(regime_encoding)
            
            # Ensure we have enough features
            if len(features) < 5:
                return None
            
            return np.array(features)
            
        except Exception as e:
            self.logger.error(f"Error extracting features: {e}")
            return None

    async def _generate_prediction(self, features: np.ndarray) -> Optional[Dict[str, Any]]:
        """Generate ML prediction for strategy composition."""
        try:
            if features is None or len(features) == 0:
                return None
            
            # Simple ML model (placeholder for actual model)
            # In production, this would use a trained model like RandomForest, Neural Network, etc.
            
            # Calculate prediction based on features
            volatility = features[0] if len(features) > 0 else 0.0
            trend_score = features[1] if len(features) > 1 else 0.0
            volume_ratio = features[2] if len(features) > 2 else 1.0
            rsi = features[3] if len(features) > 3 else 0.5
            macd = features[4] if len(features) > 4 else 0.0
            
            # Simple scoring algorithm
            score = 0.0
            
            # Volatility component (higher volatility = higher opportunity)
            if 0.1 <= volatility <= 0.5:
                score += 0.3
            elif volatility > 0.5:
                score += 0.2
            
            # Trend component
            if abs(trend_score) > 0.6:
                score += 0.3
            
            # Volume component
            if volume_ratio > 1.5:
                score += 0.2
            
            # RSI component (oversold/overbought conditions)
            if rsi < 0.3 or rsi > 0.7:
                score += 0.2
            
            # MACD component
            if abs(macd) > 0.1:
                score += 0.1
            
            # Normalize score to 0-1
            score = min(score, 1.0)
            
            # Determine strategy type based on features
            strategy_type = self._determine_strategy_type(features, score)
            
            # Calculate confidence
            confidence = score * 0.8 + 0.2  # Base confidence of 20%
            
            return {
                "score": score,
                "confidence": confidence,
                "strategy_type": strategy_type,
                "features": features.tolist()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating prediction: {e}")
            return None

    def _determine_strategy_type(self, features: np.ndarray, score: float) -> str:
        """Determine strategy type based on features and score."""
        try:
            if score < 0.3:
                return "market_making"  # Low opportunity, stable conditions
            
            # Analyze feature patterns
            volatility = features[0] if len(features) > 0 else 0.0
            trend_score = features[1] if len(features) > 1 else 0.0
            rsi = features[3] if len(features) > 3 else 0.5
            
            if volatility > 0.4 and abs(trend_score) > 0.7:
                return "trend_following"  # High volatility + strong trend
            
            if rsi < 0.3 or rsi > 0.7:
                return "mean_reversion"  # Oversold/overbought conditions
            
            if volatility < 0.2 and trend_score < 0.3:
                return "statistical_arbitrage"  # Low volatility, sideways market
            
            return "adaptive"  # Default adaptive strategy
            
        except Exception as e:
            self.logger.error(f"Error determining strategy type: {e}")
            return "adaptive"

    async def _create_ml_strategy(self, symbol: str, strategy_type: str, 
                                 prediction: Dict[str, Any], market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create ML-based strategy from prediction."""
        try:
            strategy = {
                "type": "ml_composed",
                "symbol": symbol,
                "strategy_type": prediction["strategy_type"],
                "confidence": prediction["confidence"],
                "ml_score": prediction["score"],
                "features": prediction["features"],
                "market_conditions": {
                    "volatility": float(market_data.get("volatility", 0.0)),
                    "trend_score": float(market_data.get("trend_score", 0.0)),
                    "volume_ratio": float(market_data.get("volume", 0.0)) / float(market_data.get("avg_volume", 1.0)) if market_data.get("avg_volume", 0) > 0 else 1.0
                },
                "timestamp": int(time.time()),
                "description": f"ML-composed {prediction['strategy_type']} strategy for {symbol}: confidence {prediction['confidence']:.2f}"
            }
            
            return strategy
            
        except Exception as e:
            self.logger.error(f"Error creating ML strategy: {e}")
            return None

    async def _store_composed_strategy(self, strategy: Dict[str, Any]):
        """Store composed strategy in Redis."""
        try:
            if not isinstance(strategy, dict):
                self.logger.error(f"Invalid strategy type: {type(strategy)}, expected dict")
                return
                
            strategy_id = f"{strategy['type']}:{strategy.get('symbol', 'unknown')}:{strategy['timestamp']}"
            
            # Store in Redis with proper JSON serialization
            try:
                import json
                self.redis_conn.set(
                    f"strategy_engine:ml_strategy:{strategy_id}", 
                    json.dumps(strategy), 
                    ex=604800
                )
                
                # Store in local cache
                self.composed_strategies[strategy_id] = strategy
                
                # Update model performance
                await self._update_model_performance(strategy)
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing ML strategy: {e}")
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing ML strategy: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error storing ML strategy: {e}")
            
        except Exception as e:
            self.logger.error(f"Unexpected error in _store_composed_strategy: {e}")

    async def _update_model_performance(self, strategy: Dict[str, Any]):
        """Update model performance metrics."""
        try:
            strategy_type = strategy.get("strategy_type", "unknown")
            confidence = strategy.get("confidence", 0.0)
            
            if strategy_type not in self.model_performance:
                self.model_performance[strategy_type] = []
            
            self.model_performance[strategy_type].append(confidence)
            
            # Keep only last 100 predictions per strategy type
            if len(self.model_performance[strategy_type]) > 100:
                self.model_performance[strategy_type] = self.model_performance[strategy_type][-100:]
            
        except Exception as e:
            self.logger.error(f"Error updating model performance: {e}")

    async def _update_model(self):
        """Update the ML model with new data."""
        try:
            self.logger.info("Updating ML model...")
            
            # Get latest training data
            training_data = await self._get_training_data()
            
            if len(training_data) >= self.min_data_points:
                # Update model (placeholder for actual model update)
                self.last_model_update = time.time()
                self.logger.info("ML model updated successfully")
            else:
                self.logger.warning("Insufficient data for model update")
                
        except Exception as e:
            self.logger.error(f"Error updating ML model: {e}")

    async def get_composed_strategies(self) -> List[Dict[str, Any]]:
        """Get all composed strategies."""
        try:
            return list(self.composed_strategies.values())
        except Exception as e:
            self.logger.error(f"Error getting composed strategies: {e}")
            return []

    async def get_model_performance(self) -> Dict[str, Any]:
        """Get ML model performance metrics."""
        try:
            performance = {}
            for strategy_type, confidences in self.model_performance.items():
                if confidences:
                    performance[strategy_type] = {
                        "avg_confidence": np.mean(confidences),
                        "total_predictions": len(confidences),
                        "high_confidence_rate": sum(1 for c in confidences if c > 0.8) / len(confidences)
                    }
            
            return performance
            
        except Exception as e:
            self.logger.error(f"Error getting model performance: {e}")
            return {}

    def get_composer_stats(self) -> Dict[str, Any]:
        """Get ML composer statistics."""
        return {
            **self.stats,
            "model_ready": self.model_ready,
            "composed_strategies": len(self.composed_strategies),
            "uptime": time.time() - self.stats["start_time"]
        }

    async def force_model_update(self):
        """Force immediate model update."""
        try:
            await self._update_model()
            self.logger.info("Forced model update completed")
        except Exception as e:
            self.logger.error(f"Error in forced model update: {e}")