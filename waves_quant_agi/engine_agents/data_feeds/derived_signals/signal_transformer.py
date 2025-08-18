#!/usr/bin/env python3
"""
Signal Transformer
Converts basic signals to execution-ready format with all required fields.
"""

import json
import time
from typing import Dict, Any, List, Optional
from ..utils.data_cleaner import DataCleaner
from ..utils.timestamp_utils import TimestampUtils
from ..utils.schema_validator import SchemaValidator

class SignalTransformer:
    """Transform basic signals to execution-ready format."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.cleaner = DataCleaner()
        self.timestamp_utils = TimestampUtils()
        self.validator = SchemaValidator()
        
        # Execution-ready signal schema
        self.execution_schema = {
            "symbol": str,
            "action": str,  # "buy", "sell", "hold"
            "confidence": float,  # 0 to 1
            "strategy": str,  # strategy name
            "volume": float,  # position size
            "price": float,  # entry price
            "timestamp": float,
            "source": str,  # signal source
            "execution_priority": int  # 1=HFT, 2=Fast, 3=Tactical
        }
        
        # Strategy mapping for different signal types
        self.strategy_mapping = {
            "live_trading_signals": "Live_Trading",
            "tactical_signals": "Tactical_Strategy", 
            "fast_signals": "Fast_Strategy",
            "hft_signals": "HFT_Strategy"
        }
        
        # Default position sizing
        self.default_volumes = {
            "live_trading_signals": 0.01,  # Micro lot
            "tactical_signals": 0.02,      # Mini lot
            "fast_signals": 0.01,          # Micro lot
            "hft_signals": 0.005           # Nano lot
        }
        
        # Execution priorities
        self.execution_priorities = {
            "live_trading_signals": 3,
            "tactical_signals": 3,
            "fast_signals": 2,
            "hft_signals": 1
        }

    def transform_signal(self, basic_signal: Dict[str, Any], signal_type: str) -> Optional[Dict[str, Any]]:
        """Transform a basic signal to execution-ready format."""
        try:
            # Extract basic signal data
            symbol = basic_signal.get("symbol", "Unknown")
            signal_type_field = basic_signal.get("signal_type", "hold")
            strength = basic_signal.get("strength", 0.5)
            timestamp = basic_signal.get("timestamp", time.time())
            
            # Map signal_type to action
            action = self._map_signal_type_to_action(signal_type_field)
            
            # Map strength to confidence
            confidence = self._map_strength_to_confidence(strength)
            
            # Get strategy name
            strategy = self.strategy_mapping.get(signal_type, "Unknown_Strategy")
            
            # Calculate volume based on confidence and signal type
            base_volume = self.default_volumes.get(signal_type, 0.01)
            volume = self._calculate_volume(base_volume, confidence, action)
            
            # Get current market price (placeholder - should come from market data)
            price = self._get_current_price(symbol, basic_signal)
            
            # Create execution-ready signal
            execution_signal = {
                "symbol": symbol,
                "action": action,
                "confidence": confidence,
                "strategy": strategy,
                "volume": volume,
                "price": price,
                "timestamp": timestamp,
                "source": signal_type,
                "execution_priority": self.execution_priorities.get(signal_type, 3)
            }
            
            # Validate the transformed signal
            if self.validator.validate(execution_signal, self.execution_schema):
                cleaned_signal = self.cleaner.clean(execution_signal)
                return cleaned_signal
            else:
                print(f"❌ Transformed signal validation failed for {symbol}")
                return None
                
        except Exception as e:
            print(f"❌ Error transforming signal: {e}")
            return None

    def _map_signal_type_to_action(self, signal_type: str) -> str:
        """Map signal type to execution action."""
        mapping = {
            "buy": "buy",
            "sell": "sell", 
            "hold": "hold",
            "long": "buy",
            "short": "sell",
            "neutral": "hold"
        }
        return mapping.get(signal_type.lower(), "hold")

    def _map_strength_to_confidence(self, strength: float) -> float:
        """Map signal strength to confidence score."""
        # Ensure strength is between 0 and 1
        strength = max(0.0, min(1.0, strength))
        
        # Map strength to confidence with some adjustment
        if strength < 0.3:
            confidence = strength * 1.5  # Boost low strength signals
        elif strength > 0.7:
            confidence = 0.7 + (strength - 0.7) * 0.8  # Cap high confidence
        else:
            confidence = strength
            
        return round(confidence, 3)

    def _calculate_volume(self, base_volume: float, confidence: float, action: str) -> float:
        """Calculate position size based on confidence and action."""
        if action == "hold":
            return 0.0
            
        # Scale volume by confidence
        scaled_volume = base_volume * confidence
        
        # Apply risk management limits
        min_volume = 0.001  # Minimum lot size
        max_volume = 0.1    # Maximum lot size
        
        volume = max(min_volume, min(scaled_volume, max_volume))
        
        # Round to appropriate lot size increments
        if volume < 0.01:
            volume = round(volume, 3)  # Nano lots
        elif volume < 0.1:
            volume = round(volume, 2)  # Micro lots
        else:
            volume = round(volume, 2)  # Mini lots
            
        return volume

    def _get_current_price(self, symbol: str, basic_signal: Dict[str, Any]) -> float:
        """Get current market price for the symbol."""
        # Try to get price from the basic signal first
        if "price" in basic_signal and basic_signal["price"] > 0:
            return basic_signal["price"]
        
        # Try to get price from indicators
        indicators = basic_signal.get("indicators", [])
        for indicator in indicators:
            if indicator.get("indicator") == "price":
                return indicator.get("value", 0.0)
        
        # Default prices for common symbols (fallback)
        default_prices = {
            "EURUSD": 1.0850,
            "GBPUSD": 1.2650,
            "USDJPY": 150.00,
            "XAUUSD": 2000.0,
            "BTCUSD": 45000.0,
            "ETHUSD": 2500.0
        }
        
        # Try to match symbol pattern
        for pattern, price in default_prices.items():
            if pattern in symbol or symbol in pattern:
                return price
        
        # Return a reasonable default
        return 1.0000

    def transform_signal_batch(self, basic_signals: List[Dict[str, Any]], signal_type: str) -> List[Dict[str, Any]]:
        """Transform a batch of basic signals."""
        transformed_signals = []
        
        for signal in basic_signals:
            transformed = self.transform_signal(signal, signal_type)
            if transformed:
                transformed_signals.append(transformed)
        
        return transformed_signals

    def validate_execution_signal(self, signal: Dict[str, Any]) -> bool:
        """Validate that a signal is ready for execution."""
        try:
            # Check required fields
            required_fields = ["symbol", "action", "confidence", "strategy", "volume", "price"]
            for field in required_fields:
                if field not in signal:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            # Validate action
            if signal["action"] not in ["buy", "sell", "hold"]:
                print(f"❌ Invalid action: {signal['action']}")
                return False
            
            # Validate confidence
            if not (0.0 <= signal["confidence"] <= 1.0):
                print(f"❌ Invalid confidence: {signal['confidence']}")
                return False
            
            # Validate volume
            if signal["action"] != "hold" and signal["volume"] <= 0:
                print(f"❌ Invalid volume for {signal['action']}: {signal['volume']}")
                return False
            
            # Validate price
            if signal["price"] <= 0:
                print(f"❌ Invalid price: {signal['price']}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error validating execution signal: {e}")
            return False
