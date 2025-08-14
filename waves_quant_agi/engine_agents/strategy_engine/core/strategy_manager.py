#!/usr/bin/env python3
"""
Strategy Manager - Core Strategy Management Component
Manages trading strategies and integrates with consolidated trading functionality.
Focuses purely on strategy-specific management, delegating risk management to the risk management agent.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import deque

# Import consolidated trading functionality
from ..trading.signal_processor import TradingSignalProcessor
from ..trading.flow_manager import TradingFlowManager
from ..trading.memory.trading_context import TradingContext

@dataclass
class Strategy:
    """A trading strategy."""
    strategy_id: str
    name: str
    description: str
    strategy_type: str  # arbitrage, statistical, trend_following, market_making, news_driven, htf
    symbol: str
    parameters: Dict[str, Any]
    status: str = "inactive"  # inactive, active, paused, archived
    created_at: float = None
    last_updated: float = None
    version: str = "1.0.0"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
        if self.last_updated is None:
            self.last_updated = time.time()

@dataclass
class StrategyPerformance:
    """Strategy performance metrics."""
    strategy_id: str
    total_pnl: float = 0.0
    successful_trades: int = 0
    total_trades: int = 0
    win_rate: float = 0.0
    average_pnl: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    last_updated: float = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = time.time()

class StrategyManager:
    """Manages trading strategies and integrates with consolidated trading functionality.
    
    Focuses purely on strategy-specific management:
    - Strategy registration and lifecycle management
    - Strategy parameter configuration
    - Strategy performance tracking
    - Strategy activation/deactivation
    
    Risk management is delegated to the risk management agent.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize consolidated trading components
        self.trading_signal_processor = TradingSignalProcessor(config)
        self.trading_flow_manager = TradingFlowManager(config)
        self.trading_context = TradingContext(max_history=1000)  # Fixed: pass integer instead of config
        
        # Strategy management state
        self.strategies: Dict[str, Strategy] = {}
        self.strategy_performance: Dict[str, StrategyPerformance] = {}
        self.strategy_signals: Dict[str, List[Dict[str, Any]]] = {}
        self.strategy_history: deque = deque(maxlen=10000)
        
        # Strategy management settings (strategy-specific only)
        self.strategy_settings = {
            "max_strategies": 1000,
            "max_strategies_per_symbol": 10,
            "strategy_timeout": 300,  # 5 minutes
            "performance_update_interval": 60,  # 1 minute
            "strategy_parameters": {
                "default_confidence_threshold": 0.7,
                "default_position_size": 10000,
                "default_timeout": 60
            }
        }
        
        # Strategy management statistics
        self.strategy_stats = {
            "total_strategies": 0,
            "active_strategies": 0,
            "inactive_strategies": 0,
            "total_signals": 0,
            "total_trades": 0,
            "total_pnl": 0.0
        }
        
    async def initialize(self):
        """Initialize the strategy manager."""
        try:
            # Initialize trading components
            await self.trading_signal_processor.initialize()
            await self.trading_flow_manager.initialize()
            await self.trading_context.initialize()
            
            # Load strategy settings
            await self._load_strategy_settings()
            
            # Load existing strategies
            await self._load_existing_strategies()
            
            print("✅ Strategy Manager initialized")
            
        except Exception as e:
            print(f"❌ Error initializing Strategy Manager: {e}")
            raise
    
    async def _load_strategy_settings(self):
        """Load strategy management settings from configuration."""
        try:
            strategy_config = self.config.get("strategy_engine", {}).get("strategy_management", {})
            self.strategy_settings.update(strategy_config)
        except Exception as e:
            print(f"❌ Error loading strategy settings: {e}")

    async def _load_existing_strategies(self):
        """Load existing strategies from storage."""
        try:
            # This would typically load from database or configuration
            # For now, initialize with empty state
            print("✅ No existing strategies to load")
            
        except Exception as e:
            print(f"❌ Error loading existing strategies: {e}")

    async def add_strategy(self, name: str, description: str, strategy_type: str, 
                          symbol: str, parameters: Dict[str, Any]) -> str:
        """Add a new trading strategy.
        
        This focuses purely on strategy creation, not risk management.
        """
        try:
            # Generate strategy ID
            strategy_id = f"strategy_{name.lower().replace(' ', '_')}_{int(time.time())}"
            
            # Validate strategy parameters (strategy-specific validation only)
            if not await self._validate_strategy_parameters(strategy_type, parameters):
                raise ValueError("Invalid strategy parameters")
            
            # Check strategy limits
            if len(self.strategies) >= self.strategy_settings["max_strategies"]:
                raise ValueError("Maximum number of strategies reached")
            
            symbol_strategies = [s for s in self.strategies.values() if s.symbol == symbol]
            if len(symbol_strategies) >= self.strategy_settings["max_strategies_per_symbol"]:
                raise ValueError(f"Maximum number of strategies for symbol {symbol} reached")
            
            # Create strategy
            strategy = Strategy(
                strategy_id=strategy_id,
                name=name,
                description=description,
                strategy_type=strategy_type,
                symbol=symbol,
                parameters=parameters
            )
            
            # Store strategy
            self.strategies[strategy_id] = strategy
            
            # Initialize performance tracking
            self.strategy_performance[strategy_id] = StrategyPerformance(strategy_id=strategy_id)
            
            # Initialize signal tracking
            self.strategy_signals[strategy_id] = []
            
            # Store strategy in trading context
            await self.trading_context.store_signal({
                "type": "strategy_creation",
                "strategy_id": strategy_id,
                "strategy_data": {
                    "name": name,
                    "type": strategy_type,
                    "symbol": symbol,
                    "parameters": parameters
                },
                "timestamp": int(time.time())
            })
            
            # Update statistics
            self.strategy_stats["total_strategies"] += 1
            self.strategy_stats["inactive_strategies"] += 1
            
            print(f"✅ Strategy added: {strategy_id}")
            return strategy_id
            
        except Exception as e:
            print(f"❌ Error adding strategy: {e}")
            raise

    async def _validate_strategy_parameters(self, strategy_type: str, parameters: Dict[str, Any]) -> bool:
        """Validate strategy parameters (strategy-specific validation only).
        
        This does NOT include risk management validation.
        """
        try:
            # Basic parameter validation
            if not parameters:
                return False
            
            # Strategy type validation
            valid_types = ["arbitrage", "statistical", "trend_following", "market_making", "news_driven", "htf"]
            if strategy_type not in valid_types:
                return False
            
            # Required parameters based on strategy type
            required_params = self._get_required_parameters(strategy_type)
            for param in required_params:
                if param not in parameters:
                    print(f"❌ Missing required parameter: {param}")
                    return False
            
            # Parameter value validation
            for param_name, param_value in parameters.items():
                if not self._validate_parameter_value(param_name, param_value):
                    print(f"❌ Invalid parameter value: {param_name} = {param_value}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error validating strategy parameters: {e}")
            return False

    def _get_required_parameters(self, strategy_type: str) -> List[str]:
        """Get required parameters for a strategy type."""
        required_params = {
            "arbitrage": ["spread_threshold", "execution_speed"],
            "statistical": ["lookback_period", "z_score_threshold"],
            "trend_following": ["trend_period", "trend_strength"],
            "market_making": ["spread_width", "inventory_limit"],
            "news_driven": ["sentiment_threshold", "reaction_time"],
            "htf": ["timeframe", "volatility_threshold"]
        }
        return required_params.get(strategy_type, [])

    def _validate_parameter_value(self, param_name: str, param_value: Any) -> bool:
        """Validate individual parameter values."""
        try:
            # Basic type validation
            if param_name in ["lookback_period", "trend_period", "reaction_time", "timeframe"]:
                if not isinstance(param_value, int) or param_value <= 0:
                    return False
            
            elif param_name in ["spread_threshold", "z_score_threshold", "trend_strength", 
                               "sentiment_threshold", "volatility_threshold"]:
                if not isinstance(param_value, (int, float)) or param_value <= 0:
                    return False
            
            elif param_name in ["spread_width", "inventory_limit"]:
                if not isinstance(param_value, (int, float)) or param_value < 0:
                    return False
            
            elif param_name in ["execution_speed"]:
                if not isinstance(param_value, str) or param_value not in ["ultra_fast", "fast", "normal"]:
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error validating parameter value: {e}")
            return False

    async def activate_strategy(self, strategy_id: str) -> bool:
        """Activate a strategy."""
        try:
            if strategy_id not in self.strategies:
                print(f"❌ Strategy {strategy_id} not found")
                return False
            
            strategy = self.strategies[strategy_id]
            if strategy.status == "active":
                print(f"⚠️ Strategy {strategy_id} is already active")
                return True
            
            # Update strategy status
            strategy.status = "active"
            strategy.last_updated = time.time()
            
            # Update statistics
            self.strategy_stats["active_strategies"] += 1
            self.strategy_stats["inactive_strategies"] -= 1
            
            # Store activation in trading context
            await self.trading_context.store_signal({
                "type": "strategy_activation",
                "strategy_id": strategy_id,
                "activation_data": {
                    "status": "active",
                    "timestamp": int(time.time())
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ Strategy activated: {strategy_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error activating strategy: {e}")
            return False

    async def deactivate_strategy(self, strategy_id: str) -> bool:
        """Deactivate a strategy."""
        try:
            if strategy_id not in self.strategies:
                print(f"❌ Strategy {strategy_id} not found")
                return False
            
            strategy = self.strategies[strategy_id]
            if strategy.status != "active":
                print(f"⚠️ Strategy {strategy_id} is not active")
                return True
            
            # Update strategy status
            strategy.status = "inactive"
            strategy.last_updated = time.time()
            
            # Update statistics
            self.strategy_stats["active_strategies"] -= 1
            self.strategy_stats["inactive_strategies"] += 1
            
            # Store deactivation in trading context
            await self.trading_context.store_signal({
                "type": "strategy_deactivation",
                "strategy_id": strategy_id,
                "deactivation_data": {
                    "status": "inactive",
                    "timestamp": int(time.time())
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ Strategy deactivated: {strategy_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deactivating strategy: {e}")
            return False

    async def update_strategy_parameters(self, strategy_id: str, parameters: Dict[str, Any]) -> bool:
        """Update strategy parameters."""
        try:
            if strategy_id not in self.strategies:
                print(f"❌ Strategy {strategy_id} not found")
                return False
            
            strategy = self.strategies[strategy_id]
            
            # Validate new parameters
            if not await self._validate_strategy_parameters(strategy.strategy_type, parameters):
                raise ValueError("Invalid strategy parameters")
            
            # Update parameters
            strategy.parameters.update(parameters)
            strategy.last_updated = time.time()
            
            # Store update in trading context
            await self.trading_context.store_signal({
                "type": "strategy_parameter_update",
                "strategy_id": strategy_id,
                "update_data": {
                    "parameters": parameters,
                    "timestamp": int(time.time())
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ Strategy parameters updated: {strategy_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating strategy parameters: {e}")
            return False

    async def process_strategy_signal(self, strategy_id: str, signal: Dict[str, Any]) -> bool:
        """Process a signal for a specific strategy.
        
        This focuses purely on signal processing, not risk management.
        """
        try:
            if strategy_id not in self.strategies:
                print(f"❌ Strategy {strategy_id} not found")
                return False
            
            strategy = self.strategies[strategy_id]
            if strategy.status != "active":
                print(f"⚠️ Strategy {strategy_id} is not active")
                return False
            
            # Validate signal using trading signal processor
            if not await self.trading_signal_processor.validate_trading_signal(signal):
                print(f"❌ Invalid signal for strategy {strategy_id}")
                return False
            
            # Process signal through trading flow manager
            flow_result = await self.trading_flow_manager.process_trading_signal(signal)
            
            if flow_result.get("success", False):
                # Signal processed successfully
                self.strategy_signals[strategy_id].append(signal)
                
                # Store signal in trading context
                await self.trading_context.store_signal({
                    "type": "strategy_signal_processed",
                    "strategy_id": strategy_id,
                    "signal_data": {
                        "signal": signal,
                        "flow_result": flow_result
                    },
                    "timestamp": int(time.time())
                })
                
                # Update statistics
                self.strategy_stats["total_signals"] += 1
                
                print(f"✅ Signal processed for strategy: {strategy_id}")
                return True
            else:
                print(f"❌ Signal processing failed for strategy: {strategy_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error processing strategy signal: {e}")
            return False

    async def update_strategy_performance(self, strategy_id: str, pnl: float, 
                                       trade_success: bool) -> bool:
        """Update strategy performance metrics."""
        try:
            if strategy_id not in self.strategy_performance:
                print(f"❌ Strategy performance tracking not found: {strategy_id}")
                return False
            
            performance = self.strategy_performance[strategy_id]
            
            # Update performance metrics
            performance.total_pnl += pnl
            performance.total_trades += 1
            if trade_success:
                performance.successful_trades += 1
            
            # Calculate derived metrics
            performance.win_rate = performance.successful_trades / performance.total_trades if performance.total_trades > 0 else 0.0
            performance.average_pnl = performance.total_pnl / performance.total_trades if performance.total_trades > 0 else 0.0
            
            # Update last updated timestamp
            performance.last_updated = time.time()
            
            # Store performance update in trading context
            await self.trading_context.store_signal({
                "type": "strategy_performance_update",
                "strategy_id": strategy_id,
                "performance_data": {
                    "pnl": pnl,
                    "trade_success": trade_success,
                    "total_pnl": performance.total_pnl,
                    "win_rate": performance.win_rate,
                    "total_trades": performance.total_trades
                },
                "timestamp": int(time.time())
            })
            
            # Update global statistics
            self.strategy_stats["total_pnl"] += pnl
            self.strategy_stats["total_trades"] += 1
            
            print(f"✅ Performance updated for strategy: {strategy_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating strategy performance: {e}")
            return False

    async def get_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """Get a specific strategy."""
        return self.strategies.get(strategy_id)

    async def get_all_strategies(self) -> List[Strategy]:
        """Get all strategies."""
        return list(self.strategies.values())

    async def get_strategies_by_type(self, strategy_type: str) -> List[Strategy]:
        """Get strategies by type."""
        return [s for s in self.strategies.values() if s.strategy_type == strategy_type]

    async def get_strategies_by_symbol(self, symbol: str) -> List[Strategy]:
        """Get strategies by symbol."""
        return [s for s in self.strategies.values() if s.symbol == symbol]

    async def get_active_strategies(self) -> List[Strategy]:
        """Get all active strategies."""
        return [s for s in self.strategies.values() if s.status == "active"]

    async def get_strategy_performance(self, strategy_id: str) -> Optional[StrategyPerformance]:
        """Get performance metrics for a specific strategy."""
        return self.strategy_performance.get(strategy_id)

    async def get_strategy_signals(self, strategy_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent signals for a specific strategy."""
        signals = self.strategy_signals.get(strategy_id, [])
        return signals[-limit:] if limit > 0 else signals

    async def get_strategy_summary(self) -> Dict[str, Any]:
        """Get summary of strategy management statistics."""
        try:
            return {
                "stats": self.strategy_stats,
                "strategy_count": len(self.strategies),
                "active_count": len([s for s in self.strategies.values() if s.status == "active"]),
                "inactive_count": len([s for s in self.strategies.values() if s.status == "inactive"]),
                "strategy_settings": self.strategy_settings
            }
            
        except Exception as e:
            print(f"❌ Error getting strategy summary: {e}")
            return {}

    async def cleanup(self):
        """Clean up resources."""
        try:
            await self.trading_signal_processor.cleanup()
            await self.trading_flow_manager.cleanup()
            await self.trading_context.cleanup()
            print("✅ Strategy Manager cleaned up")
        except Exception as e:
            print(f"❌ Error cleaning up Strategy Manager: {e}")
