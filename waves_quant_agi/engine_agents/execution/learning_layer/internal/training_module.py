import time
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import redis
from ...logs.execution_logger import ExecutionLogger

class TrainingModule:
    """Advanced training module for execution optimization with real-time learning."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = self._init_redis()
        self.logger = ExecutionLogger("training_module", self.redis_client)
        
        # Configuration parameters
        self.accuracy_threshold = config.get("accuracy_threshold", 0.85)
        self.min_training_samples = config.get("min_training_samples", 100)
        self.retrain_interval = config.get("retrain_interval", 3600)  # 1 hour
        self.model_update_threshold = config.get("model_update_threshold", 0.02)
        
        # Performance tracking
        self.stats = {
            "total_training_sessions": 0,
            "successful_models": 0,
            "failed_models": 0,
            "last_training_time": 0,
            "start_time": time.time()
        }

    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            return redis.Redis(
                host=self.config.get("redis_host", "localhost"),
                port=self.config.get("redis_port", 6379),
                db=self.config.get("redis_db", 0),
                decode_responses=True
            )
        except Exception as e:
            self.logger.log_error(f"Failed to initialize Redis: {e}")
            return None

    async def train_execution_model(self, training_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Train models to optimize execution behavior."""
        try:
            if training_data.empty or len(training_data) < self.min_training_samples:
                self.logger.log(f"Insufficient training data: {len(training_data)} samples")
                return []

            models = []
            symbols = training_data["symbol"].unique() if "symbol" in training_data.columns else ["default"]
            
            for symbol in symbols:
                try:
                    # Filter data for symbol
                    if "symbol" in training_data.columns:
                        symbol_data = training_data[training_data["symbol"] == symbol]
                    else:
                        symbol_data = training_data
                    
                    if len(symbol_data) < self.min_training_samples:
                        self.logger.log(f"Insufficient data for {symbol}: {len(symbol_data)} samples")
                        continue
                    
                    # Train model (placeholder for actual ML training)
                    model_result = await self._train_single_model(symbol, symbol_data)
                    
                    if model_result:
                        models.append(model_result)
                        self.stats["successful_models"] += 1
                        
                        # Store model in Redis
                        if self.redis_client:
                            try:
                                model_key = f"execution:model:{symbol}"
                                self.redis_client.hset(model_key, mapping=model_result)
                                self.redis_client.expire(model_key, 604800)  # 7 days
                            except Exception as e:
                                self.logger.log_error(f"Failed to store model in Redis: {e}")
                        
                        # Log model performance
                        self.logger.log_performance("model_training", {
                            "symbol": symbol,
                            "accuracy": model_result.get("accuracy", 0),
                            "training_samples": len(symbol_data)
                        })
                        
                        await self.notify_export(model_result)
                    else:
                        self.stats["failed_models"] += 1
                        self.logger.log_error(f"Failed to train model for {symbol}")
                        
                except Exception as e:
                    self.stats["failed_models"] += 1
                    self.logger.log_error(f"Error training model for {symbol}: {e}")
                    continue

            # Update stats
            self.stats["total_training_sessions"] += 1
            self.stats["last_training_time"] = time.time()

            # Create summary
            summary = {
                "type": "training_summary",
                "model_count": len(models),
                "successful_models": self.stats["successful_models"],
                "failed_models": self.stats["failed_models"],
                "total_samples": len(training_data),
                "timestamp": int(time.time()),
                "description": f"Trained {len(models)} execution models from {len(training_data)} samples"
            }
            
            # Store summary in Redis
            if self.redis_client:
                try:
                    self.redis_client.hset("execution:training_summary", mapping=summary)
                    self.redis_client.expire("execution:training_summary", 604800)  # 7 days
                except Exception as e:
                    self.logger.log_error(f"Failed to store training summary: {e}")
            
            # Log metrics
            self.logger.log_metric("training_sessions", self.stats["total_training_sessions"])
            self.logger.log_metric("successful_models", self.stats["successful_models"])
            self.logger.log_metric("failed_models", self.stats["failed_models"])
            
            await self.notify_core(summary)
            return models
            
        except Exception as e:
            self.logger.log_error(f"Error in train_execution_model: {e}")
            return []

    async def _train_single_model(self, symbol: str, training_data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Train a single execution model for a symbol."""
        try:
            # Extract features (placeholder - would use actual feature engineering)
            features = self._extract_features(training_data)
            
            if not features:
                return None
            
            # Simulate model training (placeholder for actual ML)
            accuracy = np.random.uniform(0.7, 0.95)
            
            # Add some realistic variation based on data quality
            data_quality = min(1.0, len(training_data) / 1000)  # Normalize data quality
            accuracy = accuracy * data_quality
            
            if accuracy >= self.accuracy_threshold:
                model = {
                    "type": "execution_model",
                    "symbol": symbol,
                    "accuracy": accuracy,
                    "training_samples": len(training_data),
                    "features_used": list(features.keys()),
                    "model_version": f"v{int(time.time())}",
                    "timestamp": int(time.time()),
                    "description": f"Trained execution model for {symbol}: Accuracy {accuracy:.2%}"
                }
                
                self.logger.log_execution("model_training", {
                    "symbol": symbol,
                    "accuracy": accuracy,
                    "samples": len(training_data),
                    "description": f"Successfully trained model for {symbol}"
                })
                
                return model
            else:
                self.logger.log_execution("model_training", {
                    "symbol": symbol,
                    "accuracy": accuracy,
                    "samples": len(training_data),
                    "description": f"Model accuracy {accuracy:.2%} below threshold {self.accuracy_threshold:.2%}"
                })
                return None
                
        except Exception as e:
            self.logger.log_error(f"Error training single model for {symbol}: {e}")
            return None

    def _extract_features(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Extract features from training data."""
        try:
            features = {}
            
            # Basic features (placeholder for actual feature engineering)
            if "execution_time" in data.columns:
                features["avg_execution_time"] = float(data["execution_time"].mean())
                features["std_execution_time"] = float(data["execution_time"].std())
            
            if "slippage" in data.columns:
                features["avg_slippage"] = float(data["slippage"].mean())
                features["max_slippage"] = float(data["slippage"].max())
            
            if "volume" in data.columns:
                features["avg_volume"] = float(data["volume"].mean())
                features["volume_std"] = float(data["volume"].std())
            
            if "price" in data.columns:
                features["price_volatility"] = float(data["price"].std())
            
            # Add market conditions if available
            if "market_condition" in data.columns:
                features["market_conditions"] = data["market_condition"].value_counts().to_dict()
            
            return features
            
        except Exception as e:
            self.logger.log_error(f"Error extracting features: {e}")
            return {}

    async def update_model(self, symbol: str, new_data: pd.DataFrame) -> bool:
        """Update an existing model with new data."""
        try:
            if new_data.empty:
                return False
            
            # Get current model
            current_model = None
            if self.redis_client:
                try:
                    model_data = self.redis_client.hgetall(f"execution:model:{symbol}")
                    if model_data:
                        current_model = model_data
                except Exception as e:
                    self.logger.log_error(f"Error getting current model: {e}")
            
            # Train new model
            new_model = await self._train_single_model(symbol, new_data)
            
            if not new_model:
                return False
            
            # Compare with current model
            if current_model:
                current_accuracy = float(current_model.get("accuracy", 0))
                new_accuracy = new_model.get("accuracy", 0)
                
                improvement = new_accuracy - current_accuracy
                
                if improvement > self.model_update_threshold:
                    # Update model
                    if self.redis_client:
                        try:
                            model_key = f"execution:model:{symbol}"
                            self.redis_client.hset(model_key, mapping=new_model)
                            self.redis_client.expire(model_key, 604800)  # 7 days
                        except Exception as e:
                            self.logger.log_error(f"Failed to update model in Redis: {e}")
                    
                    self.logger.log_execution("model_update", {
                        "symbol": symbol,
                        "old_accuracy": current_accuracy,
                        "new_accuracy": new_accuracy,
                        "improvement": improvement,
                        "description": f"Updated model for {symbol} with {improvement:.2%} improvement"
                    })
                    
                    return True
                else:
                    self.logger.log(f"Model update skipped for {symbol}: improvement {improvement:.2%} below threshold {self.model_update_threshold:.2%}")
                    return False
            else:
                # No current model, store new one
                if self.redis_client:
                    try:
                        model_key = f"execution:model:{symbol}"
                        self.redis_client.hset(model_key, mapping=new_model)
                        self.redis_client.expire(model_key, 604800)  # 7 days
                    except Exception as e:
                        self.logger.log_error(f"Failed to store new model: {e}")
                
                return True
                
        except Exception as e:
            self.logger.log_error(f"Error updating model for {symbol}: {e}")
            return False

    async def get_model_performance(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get performance metrics for a specific model."""
        try:
            if not self.redis_client:
                return None
            
            model_data = self.redis_client.hgetall(f"execution:model:{symbol}")
            if model_data:
                return {
                    "symbol": symbol,
                    "accuracy": float(model_data.get("accuracy", 0)),
                    "training_samples": int(model_data.get("training_samples", 0)),
                    "model_version": model_data.get("model_version", "unknown"),
                    "last_updated": model_data.get("timestamp", 0)
                }
            
            return None
            
        except Exception as e:
            self.logger.log_error(f"Error getting model performance for {symbol}: {e}")
            return None

    async def notify_export(self, model: Dict[str, Any]):
        """Notify Export Weights of trained model."""
        try:
            if self.redis_client:
                self.redis_client.publish("export_weights", str(model))
                self.logger.log(f"Notified export weights for model: {model.get('symbol', 'unknown')}")
        except Exception as e:
            self.logger.log_error(f"Error notifying export weights: {e}")

    async def notify_core(self, summary: Dict[str, Any]):
        """Notify Core Agent of training results."""
        try:
            if self.redis_client:
                self.redis_client.publish("execution_output", str(summary))
                self.logger.log(f"Notified core agent: {summary.get('description', 'unknown')}")
        except Exception as e:
            self.logger.log_error(f"Error notifying core agent: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get training module statistics."""
        uptime = time.time() - self.stats["start_time"]
        
        return {
            "uptime_seconds": uptime,
            "total_training_sessions": self.stats["total_training_sessions"],
            "successful_models": self.stats["successful_models"],
            "failed_models": self.stats["failed_models"],
            "success_rate": (self.stats["successful_models"] / max(self.stats["successful_models"] + self.stats["failed_models"], 1)) * 100,
            "last_training_time": self.stats["last_training_time"],
            "accuracy_threshold": self.accuracy_threshold,
            "min_training_samples": self.min_training_samples
        }