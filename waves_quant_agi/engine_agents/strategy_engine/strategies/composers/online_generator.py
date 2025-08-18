#!/usr/bin/env python3
"""
Online Generator - Strategy Online Generation Component
Generates new trading strategies online and integrates with consolidated trading functionality.
Focuses purely on strategy-specific online generation, delegating risk management to the risk management agent.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import deque

# Import consolidated trading functionality (updated paths for new structure)
from ...core.memory.trading_context import TradingContext
from ...core.learning.trading_research_engine import TradingResearchEngine

@dataclass
class GenerationRequest:
    """An online strategy generation request."""
    request_id: str
    generation_type: str  # market_adaptive, volatility_based, momentum_driven
    target_symbols: List[str]
    market_conditions: Dict[str, Any]
    priority: int = 5
    created_at: float = None
    status: str = "pending"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

@dataclass
class GenerationResult:
    """Result of online strategy generation."""
    result_id: str
    request_id: str
    generation_type: str
    generated_strategy: Dict[str, Any]
    market_conditions: Dict[str, Any]
    generation_duration: float
    timestamp: float
    success: bool

class OnlineGenerator:
    """Generates new trading strategies online based on market conditions.
    
    Focuses purely on strategy-specific online generation:
    - Market-adaptive strategy generation
    - Volatility-based strategy creation
    - Momentum-driven strategy composition
    - Real-time market condition analysis
    
    Risk management is delegated to the risk management agent.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize consolidated trading components
        self.trading_context = TradingContext(max_history=1000)
        self.trading_research_engine = TradingResearchEngine(config)
        
        # Online generation state
        self.generation_queue: deque = deque(maxlen=100)
        self.active_generations: Dict[str, GenerationRequest] = {}
        self.generation_results: Dict[str, List[GenerationResult]] = {}
        self.generation_history: deque = deque(maxlen=1000)
        
        # Online generation settings (strategy-specific only)
        self.generation_settings = {
            "max_concurrent_generations": 5,
            "generation_timeout": 1800,  # 30 minutes
            "market_analysis_depth": 100,
            "generation_types": ["market_adaptive", "volatility_based", "momentum_driven"],
            "strategy_parameters": {
                "max_components": 3,
                "min_market_data": 100,
                "adaptation_threshold": 0.1
            }
        }
        
        # Online generation statistics
        self.generation_stats = {
            "total_generations": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "total_strategies_generated": 0,
            "average_generation_time": 0.0,
            "market_adaptations": 0
        }
        
        # Logger
        self.logger = None
        
    def set_logger(self, logger):
        """Set logger for the online generator."""
        self.logger = logger
        
    async def initialize(self):
        """Initialize the online generator."""
        try:
            # Initialize trading components
            await self.trading_context.initialize()
            await self.trading_research_engine.initialize()
            
            # Load generation settings
            await self._load_generation_settings()
            
            print("✅ Online Generator initialized")
            
        except Exception as e:
            print(f"❌ Error initializing Online Generator: {e}")
            raise
    
    async def _load_generation_settings(self):
        """Load online generation settings from configuration."""
        try:
            gen_config = self.config.get("strategy_engine", {}).get("online_generation", {})
            self.generation_settings.update(gen_config)
        except Exception as e:
            print(f"❌ Error loading generation settings: {e}")

    async def add_generation_request(self, generation_type: str, target_symbols: List[str], 
                                   market_conditions: Dict[str, Any]) -> str:
        """Add an online generation request to the queue."""
        try:
            request_id = f"online_gen_{generation_type}_{int(time.time())}"
            
            request = GenerationRequest(
                request_id=request_id,
                generation_type=generation_type,
                target_symbols=target_symbols,
                market_conditions=market_conditions
            )
            
            # Add to generation queue
            self.generation_queue.append(request)
            
            # Store request in trading context
            await self.trading_context.store_signal({
                "type": "online_generation_request",
                "request_id": request_id,
                "generation_data": {
                    "type": generation_type,
                    "target_symbols": target_symbols,
                    "market_conditions": market_conditions
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ Added online generation request: {request_id}")
            return request_id
            
        except Exception as e:
            print(f"❌ Error adding online generation request: {e}")
            return ""

    async def process_generation_queue(self) -> List[GenerationResult]:
        """Process the online generation queue."""
        try:
            results = []
            
            while self.generation_queue and len(self.active_generations) < self.generation_settings["max_concurrent_generations"]:
                request = self.generation_queue.popleft()
                result = await self._execute_online_generation(request)
                if result:
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ Error processing online generation queue: {e}")
            return []

    async def _execute_online_generation(self, request: GenerationRequest) -> Optional[GenerationResult]:
        """Execute a single online generation request."""
        start_time = time.time()
        
        try:
            # Mark as active
            self.active_generations[request.request_id] = request
            request.status = "running"
            
            # Execute generation based on type
            if request.generation_type == "market_adaptive":
                generated_strategy = await self._generate_market_adaptive_strategy(request)
            elif request.generation_type == "volatility_based":
                generated_strategy = await self._generate_volatility_based_strategy(request)
            elif request.generation_type == "momentum_driven":
                generated_strategy = await self._generate_momentum_driven_strategy(request)
            else:
                raise ValueError(f"Unknown generation type: {request.generation_type}")
            
            if not generated_strategy:
                raise ValueError("Strategy generation failed")
            
            # Create generation result
            result = GenerationResult(
                result_id=f"result_{request.request_id}",
                request_id=request.request_id,
                generation_type=request.generation_type,
                generated_strategy=generated_strategy,
                market_conditions=request.market_conditions,
                generation_duration=time.time() - start_time,
                timestamp=time.time(),
                success=True
            )
            
            # Store result
            if request.generation_type not in self.generation_results:
                self.generation_results[request.generation_type] = []
            self.generation_results[request.generation_type].append(result)
            
            # Update statistics
            self.generation_stats["total_generations"] += 1
            self.generation_stats["successful_generations"] += 1
            self.generation_stats["total_strategies_generated"] += 1
            self.generation_stats["average_generation_time"] += result.generation_duration
            
            # Store result in trading context
            await self.trading_context.store_signal({
                "type": "online_generation_result",
                "generation_type": request.generation_type,
                "result_data": {
                    "strategy": generated_strategy,
                    "market_conditions": request.market_conditions
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ Online generation completed: {request.request_id}")
            return result
            
        except Exception as e:
            print(f"❌ Error executing online generation: {e}")
            self.generation_stats["failed_generations"] += 1
            
            # Return failed result
            return GenerationResult(
                result_id=f"failed_{request.request_id}",
                request_id=request.request_id,
                generation_type=request.generation_type,
                generated_strategy={},
                market_conditions=request.market_conditions,
                generation_duration=time.time() - start_time,
                timestamp=time.time(),
                success=False
            )
        finally:
            # Remove from active generations
            self.active_generations.pop(request.request_id, None)

    async def _generate_market_adaptive_strategy(self, request: GenerationRequest) -> Optional[Dict[str, Any]]:
        """Generate a market-adaptive strategy."""
        try:
            # Analyze current market conditions
            market_analysis = await self._analyze_market_conditions(request.target_symbols)
            
            # Identify market regime
            market_regime = self._identify_market_regime(market_analysis)
            
            # Generate adaptive components
            strategy_components = self._generate_market_adaptive_components(market_regime, market_analysis)
            
            # Compose strategy
            strategy = {
                "strategy_id": f"market_adaptive_{request.request_id}",
                "name": f"Market Adaptive Strategy {request.request_id}",
                "description": "Online-generated market-adaptive trading strategy",
                "strategy_type": "market_adaptive",
                "symbols": request.target_symbols,
                "components": strategy_components,
                "parameters": self._generate_adaptive_parameters(market_regime),
                "market_regime": market_regime,
                "adaptation_threshold": 0.1,
                "created_at": time.time()
            }
            
            return strategy
            
        except Exception as e:
            print(f"❌ Error generating market-adaptive strategy: {e}")
            return None

    async def _generate_volatility_based_strategy(self, request: GenerationRequest) -> Optional[Dict[str, Any]]:
        """Generate a volatility-based strategy."""
        try:
            # Analyze volatility patterns
            volatility_analysis = await self._analyze_volatility_patterns(request.target_symbols)
            
            # Identify volatility regime
            volatility_regime = self._identify_volatility_regime(volatility_analysis)
            
            # Generate volatility-based components
            strategy_components = self._generate_volatility_based_components(volatility_regime, volatility_analysis)
            
            # Compose strategy
            strategy = {
                "strategy_id": f"volatility_based_{request.request_id}",
                "name": f"Volatility-Based Strategy {request.request_id}",
                "description": "Online-generated volatility-based trading strategy",
                "strategy_type": "volatility_based",
                "symbols": request.target_symbols,
                "components": strategy_components,
                "parameters": self._generate_volatility_parameters(volatility_regime),
                "volatility_regime": volatility_regime,
                "volatility_threshold": 0.15,
                "created_at": time.time()
            }
            
            return strategy
            
        except Exception as e:
            print(f"❌ Error generating volatility-based strategy: {e}")
            return None

    async def _generate_momentum_driven_strategy(self, request: GenerationRequest) -> Optional[Dict[str, Any]]:
        """Generate a momentum-driven strategy."""
        try:
            # Analyze momentum patterns
            momentum_analysis = await self._analyze_momentum_patterns(request.target_symbols)
            
            # Identify momentum regime
            momentum_regime = self._identify_momentum_regime(momentum_analysis)
            
            # Generate momentum-driven components
            strategy_components = self._generate_momentum_driven_components(momentum_regime, momentum_analysis)
            
            # Compose strategy
            strategy = {
                "strategy_id": f"momentum_driven_{request.request_id}",
                "name": f"Momentum-Driven Strategy {request.request_id}",
                "description": "Online-generated momentum-driven trading strategy",
                "strategy_type": "momentum_driven",
                "symbols": request.target_symbols,
                "components": strategy_components,
                "parameters": self._generate_momentum_parameters(momentum_regime),
                "momentum_regime": momentum_regime,
                "momentum_threshold": 0.02,
                "created_at": time.time()
            }
            
            return strategy
            
        except Exception as e:
            print(f"❌ Error generating momentum-driven strategy: {e}")
            return None

    async def _analyze_market_conditions(self, target_symbols: List[str]) -> Dict[str, Any]:
        """Analyze current market conditions."""
        try:
            market_analysis = {}
            
            for symbol in target_symbols:
                # Get recent market data from trading context
                signals = await self.trading_context.get_recent_signals(symbol, limit=100)
                pnl_snapshots = await self.trading_context.get_recent_pnl_snapshots(symbol, limit=100)
                
                # Analyze market patterns
                pattern_analysis = await self.trading_research_engine.analyze_trading_patterns(signals + pnl_snapshots)
                
                market_analysis[symbol] = pattern_analysis
            
            return market_analysis
            
        except Exception as e:
            print(f"❌ Error analyzing market conditions: {e}")
            return {}

    async def _analyze_volatility_patterns(self, target_symbols: List[str]) -> Dict[str, Any]:
        """Analyze volatility patterns."""
        try:
            volatility_analysis = {}
            
            for symbol in target_symbols:
                # Get recent market data
                signals = await self.trading_context.get_recent_signals(symbol, limit=100)
                
                # Calculate volatility metrics
                volatility_metrics = self._calculate_volatility_metrics(signals)
                volatility_analysis[symbol] = volatility_metrics
            
            return volatility_analysis
            
        except Exception as e:
            print(f"❌ Error analyzing volatility patterns: {e}")
            return {}

    async def _analyze_momentum_patterns(self, target_symbols: List[str]) -> Dict[str, Any]:
        """Analyze momentum patterns."""
        try:
            momentum_analysis = {}
            
            for symbol in target_symbols:
                # Get recent market data
                signals = await self.trading_context.get_recent_signals(symbol, limit=100)
                
                # Calculate momentum metrics
                momentum_metrics = self._calculate_momentum_metrics(signals)
                momentum_analysis[symbol] = momentum_metrics
            
            return momentum_analysis
            
        except Exception as e:
            print(f"❌ Error analyzing momentum patterns: {e}")
            return {}

    def _identify_market_regime(self, market_analysis: Dict[str, Any]) -> str:
        """Identify current market regime."""
        try:
            # Simple market regime identification
            total_signals = sum(len(analysis.get("signals", [])) for analysis in market_analysis.values())
            
            if total_signals == 0:
                return "unknown"
            
            # Count different signal types
            signal_types = {}
            for analysis in market_analysis.values():
                for signal in analysis.get("signals", []):
                    signal_type = signal.get("type", "unknown")
                    signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
            
            # Determine regime based on signal distribution
            if signal_types.get("trend", 0) > total_signals * 0.6:
                return "trending"
            elif signal_types.get("volatile", 0) > total_signals * 0.6:
                return "volatile"
            elif signal_types.get("sideways", 0) > total_signals * 0.6:
                return "sideways"
            else:
                return "mixed"
                
        except Exception as e:
            print(f"❌ Error identifying market regime: {e}")
            return "unknown"

    def _identify_volatility_regime(self, volatility_analysis: Dict[str, Any]) -> str:
        """Identify current volatility regime."""
        try:
            # Simple volatility regime identification
            avg_volatility = 0.0
            count = 0
            
            for analysis in volatility_analysis.values():
                if "volatility" in analysis:
                    avg_volatility += analysis["volatility"]
                    count += 1
            
            if count == 0:
                return "unknown"
            
            avg_volatility /= count
            
            if avg_volatility > 0.25:
                return "high_volatility"
            elif avg_volatility > 0.15:
                return "medium_volatility"
            else:
                return "low_volatility"
                
        except Exception as e:
            print(f"❌ Error identifying volatility regime: {e}")
            return "unknown"

    def _identify_momentum_regime(self, momentum_analysis: Dict[str, Any]) -> str:
        """Identify current momentum regime."""
        try:
            # Simple momentum regime identification
            avg_momentum = 0.0
            count = 0
            
            for analysis in momentum_analysis.values():
                if "momentum" in analysis:
                    avg_momentum += analysis["momentum"]
                    count += 1
            
            if count == 0:
                return "unknown"
            
            avg_momentum /= count
            
            if abs(avg_momentum) > 0.05:
                return "strong_momentum"
            elif abs(avg_momentum) > 0.02:
                return "moderate_momentum"
            else:
                return "weak_momentum"
                
        except Exception as e:
            print(f"❌ Error identifying momentum regime: {e}")
            return "unknown"

    def _generate_market_adaptive_components(self, market_regime: str, 
                                          market_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate market-adaptive strategy components."""
        try:
            components = []
            
            # Generate components based on market regime
            if market_regime == "trending":
                components.append({
                    "component_id": "trend_follower",
                    "name": "Trend Follower",
                    "component_type": "trend_following",
                    "parameters": {"trend_period": 20, "trend_strength": 0.6},
                    "weight": 1.0
                })
            
            elif market_regime == "volatile":
                components.append({
                    "component_id": "volatility_trader",
                    "name": "Volatility Trader",
                    "component_type": "volatility_trading",
                    "parameters": {"volatility_threshold": 0.2, "mean_reversion": True},
                    "weight": 1.0
                })
            
            elif market_regime == "sideways":
                components.append({
                    "component_id": "range_trader",
                    "name": "Range Trader",
                    "component_type": "range_trading",
                    "parameters": {"range_period": 50, "breakout_threshold": 0.02},
                    "weight": 1.0
                })
            
            return components
            
        except Exception as e:
            print(f"❌ Error generating market-adaptive components: {e}")
            return []

    def _generate_volatility_based_components(self, volatility_regime: str, 
                                            volatility_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate volatility-based strategy components."""
        try:
            components = []
            
            # Generate components based on volatility regime
            if volatility_regime == "high_volatility":
                components.append({
                    "component_id": "volatility_breakout",
                    "name": "Volatility Breakout",
                    "component_type": "breakout_trading",
                    "parameters": {"volatility_threshold": 0.25, "breakout_multiplier": 2.0},
                    "weight": 1.0
                })
            
            elif volatility_regime == "medium_volatility":
                components.append({
                    "component_id": "volatility_mean_reversion",
                    "name": "Volatility Mean Reversion",
                    "component_type": "mean_reversion",
                    "parameters": {"volatility_threshold": 0.15, "reversion_strength": 0.8},
                    "weight": 1.0
                })
            
            elif volatility_regime == "low_volatility":
                components.append({
                    "component_id": "volatility_momentum",
                    "name": "Volatility Momentum",
                    "component_type": "momentum_trading",
                    "parameters": {"volatility_threshold": 0.1, "momentum_period": 10},
                    "weight": 1.0
                })
            
            return components
            
        except Exception as e:
            print(f"❌ Error generating volatility-based components: {e}")
            return []

    def _generate_momentum_driven_components(self, momentum_regime: str, 
                                           momentum_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate momentum-driven strategy components."""
        try:
            components = []
            
            # Generate components based on momentum regime
            if momentum_regime == "strong_momentum":
                components.append({
                    "component_id": "momentum_follower",
                    "name": "Momentum Follower",
                    "component_type": "momentum_following",
                    "parameters": {"momentum_period": 5, "momentum_threshold": 0.05},
                    "weight": 1.0
                })
            
            elif momentum_regime == "moderate_momentum":
                components.append({
                    "component_id": "momentum_oscillator",
                    "name": "Momentum Oscillator",
                    "component_type": "oscillator_trading",
                    "parameters": {"momentum_period": 10, "oscillator_threshold": 0.02},
                    "weight": 1.0
                })
            
            elif momentum_regime == "weak_momentum":
                components.append({
                    "component_id": "momentum_reversal",
                    "name": "Momentum Reversal",
                    "component_type": "reversal_trading",
                    "parameters": {"momentum_period": 15, "reversal_threshold": 0.01},
                    "weight": 1.0
                })
            
            return components
            
        except Exception as e:
            print(f"❌ Error generating momentum-driven components: {e}")
            return []

    def _generate_adaptive_parameters(self, market_regime: str) -> Dict[str, Any]:
        """Generate parameters for market-adaptive strategy."""
        try:
            base_params = {
                "confidence_threshold": 0.7,
                "execution_timeout": 60,
                "max_position_size": 100000
            }
            
            # Add regime-specific parameters
            if market_regime == "trending":
                base_params.update({
                    "trend_following": True,
                    "trend_period": 20,
                    "trend_strength": 0.6
                })
            elif market_regime == "volatile":
                base_params.update({
                    "volatility_trading": True,
                    "volatility_threshold": 0.2,
                    "mean_reversion": True
                })
            elif market_regime == "sideways":
                base_params.update({
                    "range_trading": True,
                    "range_period": 50,
                    "breakout_threshold": 0.02
                })
            
            return base_params
            
        except Exception as e:
            print(f"❌ Error generating adaptive parameters: {e}")
            return {}

    def _generate_volatility_parameters(self, volatility_regime: str) -> Dict[str, Any]:
        """Generate parameters for volatility-based strategy."""
        try:
            base_params = {
                "confidence_threshold": 0.7,
                "execution_timeout": 60,
                "max_position_size": 100000
            }
            
            # Add regime-specific parameters
            if volatility_regime == "high_volatility":
                base_params.update({
                    "volatility_threshold": 0.25,
                    "breakout_multiplier": 2.0,
                    "risk_management": "aggressive"
                })
            elif volatility_regime == "medium_volatility":
                base_params.update({
                    "volatility_threshold": 0.15,
                    "reversion_strength": 0.8,
                    "risk_management": "moderate"
                })
            elif volatility_regime == "low_volatility":
                base_params.update({
                    "volatility_threshold": 0.1,
                    "momentum_period": 10,
                    "risk_management": "conservative"
                })
            
            return base_params
            
        except Exception as e:
            print(f"❌ Error generating volatility parameters: {e}")
            return {}

    def _generate_momentum_parameters(self, momentum_regime: str) -> Dict[str, Any]:
        """Generate parameters for momentum-driven strategy."""
        try:
            base_params = {
                "confidence_threshold": 0.7,
                "execution_timeout": 60,
                "max_position_size": 100000
            }
            
            # Add regime-specific parameters
            if momentum_regime == "strong_momentum":
                base_params.update({
                    "momentum_period": 5,
                    "momentum_threshold": 0.05,
                    "position_sizing": "aggressive"
                })
            elif momentum_regime == "moderate_momentum":
                base_params.update({
                    "momentum_period": 10,
                    "oscillator_threshold": 0.02,
                    "position_sizing": "moderate"
                })
            elif momentum_regime == "weak_momentum":
                base_params.update({
                    "momentum_period": 15,
                    "reversal_threshold": 0.01,
                    "position_sizing": "conservative"
                })
            
            return base_params
            
        except Exception as e:
            print(f"❌ Error generating momentum parameters: {e}")
            return {}

    def _calculate_volatility_metrics(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate volatility metrics from signals."""
        try:
            if not signals:
                return {"volatility": 0.0, "volatility_type": "unknown"}
            
            # Simple volatility calculation
            prices = [s.get("price", 0.0) for s in signals if s.get("price")]
            if len(prices) < 2:
                return {"volatility": 0.0, "volatility_type": "unknown"}
            
            # Calculate price changes
            price_changes = [abs(prices[i] - prices[i-1]) for i in range(1, len(prices))]
            avg_change = sum(price_changes) / len(price_changes)
            
            return {
                "volatility": avg_change,
                "volatility_type": "price_based"
            }
            
        except Exception as e:
            print(f"❌ Error calculating volatility metrics: {e}")
            return {"volatility": 0.0, "volatility_type": "unknown"}

    def _calculate_momentum_metrics(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate momentum metrics from signals."""
        try:
            if not signals:
                return {"momentum": 0.0, "momentum_type": "unknown"}
            
            # Simple momentum calculation
            prices = [s.get("price", 0.0) for s in signals if s.get("price")]
            if len(prices) < 2:
                return {"momentum": 0.0, "momentum_type": "unknown"}
            
            # Calculate momentum (price change over time)
            momentum = (prices[-1] - prices[0]) / len(prices)
            
            return {
                "momentum": momentum,
                "momentum_type": "price_based"
            }
            
        except Exception as e:
            print(f"❌ Error calculating momentum metrics: {e}")
            return {"momentum": 0.0, "momentum_type": "unknown"}

    async def generate_strategy(self, generation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a new trading strategy online based on market conditions."""
        try:
            start_time = time.time()
            
            # Create generation request
            request = GenerationRequest(
                request_id=generation_request.get("request_id", f"online_gen_{int(time.time())}"),
                generation_type=generation_request.get("generation_type", "market_adaptive"),
                target_symbols=generation_request.get("target_symbols", ["BTC", "ETH"]),
                market_conditions=generation_request.get("market_conditions", {}),
                priority=generation_request.get("priority", 5)
            )
            
            # Add to generation queue
            self.generation_queue.append(request)
            self.active_generations[request.request_id] = request
            
            # Generate strategy based on type
            if request.generation_type == "market_adaptive":
                strategy = await self._generate_market_adaptive_strategy(request)
            elif request.generation_type == "volatility_based":
                strategy = await self._generate_volatility_based_strategy(request)
            elif request.generation_type == "momentum_driven":
                strategy = await self._generate_momentum_driven_strategy(request)
            else:
                strategy = await self._generate_market_adaptive_strategy(request)  # Default
            
            if not strategy:
                return {
                    "success": False,
                    "reason": "Failed to generate strategy"
                }
            
            # Create generation result
            generation_duration = time.time() - start_time
            result = GenerationResult(
                result_id=f"result_{request.request_id}",
                request_id=request.request_id,
                generation_type=request.generation_type,
                generated_strategy=strategy,
                market_conditions=request.market_conditions,
                generation_duration=generation_duration,
                timestamp=time.time(),
                success=True
            )
            
            # Store result
            if request.generation_type not in self.generation_results:
                self.generation_results[request.generation_type] = []
            self.generation_results[request.generation_type].append(result)
            
            # Update statistics
            self.generation_stats["total_generations"] += 1
            self.generation_stats["successful_generations"] += 1
            self.generation_stats["total_strategies_generated"] += 1
            self.generation_stats["total_generation_time"] += generation_duration
            
            # Remove from active generations
            if request.request_id in self.active_generations:
                del self.active_generations[request.request_id]
            
            return {
                "success": True,
                "result_id": result.result_id,
                "generated_strategy": strategy,
                "market_conditions": request.market_conditions,
                "generation_duration": generation_duration
            }
            
        except Exception as e:
            print(f"❌ Error generating strategy: {e}")
            return {
                "success": False,
                "reason": f"Strategy generation error: {str(e)}"
            }

    async def get_generation_status(self, generation_type: str = None) -> Dict[str, Any]:
        """Get online generation status and statistics."""
        if generation_type:
            return {
                "generation_type": generation_type,
                "active_generations": len([r for r in self.active_generations.values() if r.generation_type == generation_type]),
                "generation_results": len(self.generation_results.get(generation_type, [])),
                "last_generation": self.generation_results.get(generation_type, [{}])[-1] if self.generation_results.get(generation_type) else {}
            }
        else:
            # Calculate average generation time
            if self.generation_stats["successful_generations"] > 0:
                avg_generation_time = self.generation_stats["average_generation_time"] / self.generation_stats["successful_generations"]
            else:
                avg_generation_time = 0.0
            
            return {
                "stats": {**self.generation_stats, "average_generation_time": avg_generation_time},
                "queue_size": len(self.generation_queue),
                "active_generations": len(self.active_generations),
                "generation_history_size": len(self.generation_history),
                "generation_settings": self.generation_settings
            }

    async def get_generation_results(self, generation_type: str) -> List[GenerationResult]:
        """Get online generation results for a specific type."""
        return self.generation_results.get(generation_type, [])

    async def cleanup(self):
        """Clean up resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
            print("✅ Online Generator cleaned up")
        except Exception as e:
            print(f"❌ Error cleaning up Online Generator: {e}")