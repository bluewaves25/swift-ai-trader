"""
Machine Learning Models for Waves Quant AGI
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class TradingModel:
    """Base class for trading models"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.is_trained = False
        
    def train(self, data: pd.DataFrame) -> bool:
        """Train the model"""
        raise NotImplementedError("Subclasses must implement train method")
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        raise NotImplementedError("Subclasses must implement predict method")
    
    def evaluate(self, data: pd.DataFrame) -> Dict[str, float]:
        """Evaluate model performance"""
        raise NotImplementedError("Subclasses must implement evaluate method")

class SimpleMovingAverageModel(TradingModel):
    """Simple Moving Average trading model"""
    
    def __init__(self, short_window: int = 10, long_window: int = 30):
        super().__init__("SimpleMovingAverage", "1.0.0")
        self.short_window = short_window
        self.long_window = long_window
        self.is_trained = False
        
    def train(self, data: pd.DataFrame) -> bool:
        """Train the model (for SMA, just validate data)"""
        if 'close' not in data.columns:
            logger.error("Data must contain 'close' column")
            return False
        
        if len(data) < self.long_window:
            logger.error(f"Data length {len(data)} must be >= long_window {self.long_window}")
            return False
            
        self.is_trained = True
        logger.info(f"SMA model trained with {len(data)} data points")
        return True
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Generate trading signals based on SMA crossover"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
            
        if 'close' not in data.columns:
            raise ValueError("Data must contain 'close' column")
        
        # Calculate moving averages
        short_ma = data['close'].rolling(window=self.short_window).mean()
        long_ma = data['close'].rolling(window=self.long_window).mean()
        
        # Generate signals: 1 for buy, -1 for sell, 0 for hold
        signals = np.zeros(len(data))
        signals[short_ma > long_ma] = 1  # Buy signal
        signals[short_ma < long_ma] = -1  # Sell signal
        
        return signals
    
    def evaluate(self, data: pd.DataFrame) -> Dict[str, float]:
        """Evaluate model performance"""
        if not self.is_trained:
            return {"error": "Model not trained"}
            
        signals = self.predict(data)
        
        # Calculate basic metrics
        buy_signals = np.sum(signals == 1)
        sell_signals = np.sum(signals == -1)
        hold_signals = np.sum(signals == 0)
        
        return {
            "buy_signals": float(buy_signals),
            "sell_signals": float(sell_signals),
            "hold_signals": float(hold_signals),
            "total_signals": float(len(signals))
        }

class ModelRegistry:
    """Registry for managing trading models"""
    
    def __init__(self):
        self.models: Dict[str, TradingModel] = {}
        
    def register_model(self, model: TradingModel) -> None:
        """Register a model"""
        self.models[model.name] = model
        logger.info(f"Registered model: {model.name}")
        
    def get_model(self, name: str) -> Optional[TradingModel]:
        """Get a model by name"""
        return self.models.get(name)
        
    def list_models(self) -> List[str]:
        """List all registered models"""
        return list(self.models.keys())
        
    def remove_model(self, name: str) -> bool:
        """Remove a model"""
        if name in self.models:
            del self.models[name]
            logger.info(f"Removed model: {name}")
            return True
        return False

# Global model registry
model_registry = ModelRegistry()

# Register default models
default_sma_model = SimpleMovingAverageModel()
model_registry.register_model(default_sma_model)
