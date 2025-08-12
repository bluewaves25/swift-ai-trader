#!/usr/bin/env python3
"""
Strategy Composer - RARE COMPOSITION MODULE  
Handles rare strategy composition (1% of Strategy Engine's work)
Separated from application logic for better manageability

REFACTORED FOR SIMPLICITY:
- Only used when market conditions require new strategies
- Triggered rarely (every 5+ minutes)
- Clean separation from main application logic
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from engine_agents.shared_utils import get_shared_logger, get_agent_learner, LearningType, get_shared_redis

class StrategyComposer:
    """
    Rare strategy composition engine - handles 1% of strategy work.
    Only activated when market conditions require new strategy creation.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "composer")
        self.learner = get_agent_learner("strategy_engine", LearningType.STRATEGY_ADAPTATION, 6)
        self.redis_conn = get_shared_redis()
        
        # Composition state
        self.composition_stats = {
            "compositions_triggered": 0,
            "strategies_created": 0,
            "successful_compositions": 0,
            "failed_compositions": 0,
            "last_composition": 0
        }
        
        # Composition triggers
        self.composition_triggers = {
            "market_regime_change": False,
            "poor_performance": False,
            "new_market_conditions": False,
            "forced_composition": False
        }
        
        # Minimum time between compositions (prevents overcomposition)
        self.min_composition_interval = config.get("min_composition_interval", 300)  # 5 minutes
        
        # Strategy composition parameters
        self.regime_change_threshold = config.get("regime_change_threshold", 0.7)
        self.performance_threshold = config.get("performance_threshold", 0.5)
        self.new_conditions_threshold = config.get("new_conditions_threshold", 0.6)
        
    async def check_composition_needed(self, market_data: Dict[str, Any], 
                                     performance_data: Dict[str, Any]) -> bool:
        """
        Check if strategy composition is needed.
        This should be called rarely (every 5+ minutes).
        """
        
        # Check minimum time interval
        current_time = time.time()
        if (current_time - self.composition_stats.get("last_composition", 0)) < self.min_composition_interval:
            return False
        
        composition_needed = False
        
        # Trigger 1: Market regime change detected
        if await self._detect_regime_change(market_data):
            self.composition_triggers["market_regime_change"] = True
            composition_needed = True
            self.logger.info("Composition triggered: Market regime change detected")
        
        # Trigger 2: Poor performance across strategies
        if await self._detect_poor_performance(performance_data):
            self.composition_triggers["poor_performance"] = True
            composition_needed = True
            self.logger.info("Composition triggered: Poor strategy performance")
        
        # Trigger 3: New market conditions not covered by existing strategies
        if await self._detect_new_conditions(market_data):
            self.composition_triggers["new_market_conditions"] = True
            composition_needed = True
            self.logger.info("Composition triggered: New market conditions")
        
        return composition_needed
    
    async def compose_strategy(self, trigger_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Compose a new strategy based on current market conditions.
        This is the rare composition process.
        """
        start_time = time.time()
        
        try:
            self.logger.info("Starting strategy composition process...")
            
            # Analyze current market conditions
            market_analysis = await self._analyze_market_conditions(trigger_data)
            
            # Identify strategy gaps
            strategy_gaps = await self._identify_strategy_gaps(market_analysis)
            
            # Compose new strategy if gap exists
            new_strategy = await self._create_new_strategy(strategy_gaps, market_analysis)
            
            if new_strategy:
                # Validate the new strategy
                validated_strategy = await self._validate_strategy(new_strategy, market_analysis)
                
                if validated_strategy:
                    # Record successful composition
                    duration = time.time() - start_time
                    self._record_composition(True, duration)
                    
                    self.composition_stats["strategies_created"] += 1
                    self.composition_stats["successful_compositions"] += 1
                    
                    # Learn from composition
                    await self._learn_from_composition(new_strategy, market_analysis, duration)
                    
                    self.logger.info(f"Successfully composed strategy: {new_strategy.get('name', 'Unknown')}")
                    return validated_strategy
                else:
                    self.logger.warning("Strategy validation failed")
                    self._record_composition(False, time.time() - start_time)
                    self.composition_stats["failed_compositions"] += 1
            else:
                self.logger.info("No strategy gaps identified")
                self._record_composition(False, time.time() - start_time)
                self.composition_stats["failed_compositions"] += 1
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error in strategy composition: {e}")
            self._record_composition(False, time.time() - start_time)
            self.composition_stats["failed_compositions"] += 1
            return None

    async def _detect_regime_change(self, market_data: Dict[str, Any]) -> bool:
        """Detect if market regime has changed significantly."""
        try:
            if not market_data:
                return False
            
            # Get current market regime from Redis
            current_regime = await self._get_current_market_regime()
            previous_regime = await self._get_previous_market_regime()
            
            if not current_regime or not previous_regime:
                return False
            
            # Calculate regime change score
            regime_change_score = self._calculate_regime_change_score(current_regime, previous_regime)
            
            return regime_change_score > self.regime_change_threshold
            
        except Exception as e:
            self.logger.error(f"Error detecting regime change: {e}")
            return False

    async def _detect_poor_performance(self, performance_data: Dict[str, Any]) -> bool:
        """Detect if strategies are performing poorly."""
        try:
            if not performance_data:
                return False
            
            # Get performance metrics from Redis
            performance_metrics = await self._get_performance_metrics()
            
            if not performance_metrics:
                return False
            
            # Calculate overall performance score
            overall_score = self._calculate_overall_performance(performance_metrics)
            
            return overall_score < self.performance_threshold
            
        except Exception as e:
            self.logger.error(f"Error detecting poor performance: {e}")
            return False

    async def _detect_new_conditions(self, market_data: Dict[str, Any]) -> bool:
        """Detect new market conditions not covered by existing strategies."""
        try:
            if not market_data:
                return False
            
            # Get current market conditions
            current_conditions = await self._get_current_market_conditions()
            
            # Get existing strategy coverage
            strategy_coverage = await self._get_strategy_coverage()
            
            # Calculate coverage gap
            coverage_gap = self._calculate_coverage_gap(current_conditions, strategy_coverage)
            
            return coverage_gap > self.new_conditions_threshold
            
        except Exception as e:
            self.logger.error(f"Error detecting new conditions: {e}")
            return False

    async def _analyze_market_conditions(self, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current market conditions for strategy composition."""
        try:
            analysis = {
                "timestamp": int(time.time()),
                "market_regime": await self._get_current_market_regime(),
                "volatility_level": await self._get_volatility_level(),
                "trend_strength": await self._get_trend_strength(),
                "volume_profile": await self._get_volume_profile(),
                "correlation_matrix": await self._get_correlation_matrix(),
                "risk_metrics": await self._get_risk_metrics()
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing market conditions: {e}")
            return {}

    async def _identify_strategy_gaps(self, market_analysis: Dict[str, Any]) -> List[str]:
        """Identify gaps in current strategy coverage."""
        try:
            gaps = []
            
            # Check for missing strategy types
            current_strategies = await self._get_current_strategies()
            required_strategies = self._get_required_strategies(market_analysis)
            
            for strategy in required_strategies:
                if strategy not in current_strategies:
                    gaps.append(strategy)
            
            # Check for performance gaps
            performance_gaps = await self._identify_performance_gaps()
            gaps.extend(performance_gaps)
            
            return gaps
            
        except Exception as e:
            self.logger.error(f"Error identifying strategy gaps: {e}")
            return []

    async def _create_new_strategy(self, strategy_gaps: List[str], 
                                 market_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new strategy to fill identified gaps."""
        try:
            if not strategy_gaps:
                return None
            
            # Select the most critical gap
            critical_gap = self._select_critical_gap(strategy_gaps, market_analysis)
            
            # Generate strategy parameters
            strategy_params = self._generate_strategy_parameters(critical_gap, market_analysis)
            
            # Create strategy structure
            new_strategy = {
                "name": f"composed_{critical_gap}_{int(time.time())}",
                "type": critical_gap,
                "parameters": strategy_params,
                "market_conditions": market_analysis,
                "composition_trigger": self._get_active_triggers(),
                "timestamp": int(time.time()),
                "status": "composed"
            }
            
            return new_strategy
            
        except Exception as e:
            self.logger.error(f"Error creating new strategy: {e}")
            return None

    def _generate_strategy_parameters(self, strategy_type: str, 
                                   market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate parameters for a new strategy based on market conditions."""
        try:
            base_params = {
                "confidence_threshold": 0.6,
                "risk_tolerance": 0.5,
                "position_size": 0.1,
                "stop_loss": 0.05,
                "take_profit": 0.15
            }
            
            # Adjust parameters based on market conditions
            if market_analysis.get("volatility_level") == "high":
                base_params["stop_loss"] = 0.08
                base_params["take_profit"] = 0.20
            
            if market_analysis.get("trend_strength") == "strong":
                base_params["confidence_threshold"] = 0.7
                base_params["position_size"] = 0.15
            
            # Strategy-specific adjustments
            if strategy_type == "trend_following":
                base_params["trend_following"] = True
                base_params["momentum_threshold"] = 0.6
            elif strategy_type == "mean_reversion":
                base_params["mean_reversion"] = True
                base_params["reversion_threshold"] = 0.7
            elif strategy_type == "volatility_trading":
                base_params["volatility_trading"] = True
                base_params["volatility_threshold"] = 0.5
            
            return base_params
            
        except Exception as e:
            self.logger.error(f"Error generating strategy parameters: {e}")
            return {}

    async def _validate_strategy(self, strategy: Dict[str, Any], 
                               market_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate the composed strategy."""
        try:
            # Basic validation
            required_fields = ["name", "type", "parameters", "timestamp"]
            for field in required_fields:
                if field not in strategy:
                    self.logger.error(f"Missing required field: {field}")
                    return None
            
            # Parameter validation
            if not self._validate_strategy_parameters(strategy["parameters"]):
                self.logger.error("Strategy parameters validation failed")
                return None
            
            # Market condition validation
            if not self._validate_market_conditions(strategy, market_analysis):
                self.logger.error("Market conditions validation failed")
                return None
            
            # Store validated strategy in Redis
            await self._store_composed_strategy(strategy)
            
            return strategy
            
        except Exception as e:
            self.logger.error(f"Error validating strategy: {e}")
            return None

    def _validate_strategy_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate strategy parameters."""
        try:
            required_params = ["confidence_threshold", "risk_tolerance", "position_size"]
            for param in required_params:
                if param not in parameters:
                    return False
                
                value = parameters[param]
                if not isinstance(value, (int, float)) or value < 0:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating parameters: {e}")
            return False

    def _validate_market_conditions(self, strategy: Dict[str, Any], 
                                  market_analysis: Dict[str, Any]) -> bool:
        """Validate market conditions for strategy."""
        try:
            if not market_analysis:
                return False
            
            # Check if market analysis has required fields
            required_fields = ["market_regime", "volatility_level", "trend_strength"]
            for field in required_fields:
                if field not in market_analysis:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating market conditions: {e}")
            return False

    async def _store_composed_strategy(self, strategy: Dict[str, Any]):
        """Store composed strategy in Redis."""
        try:
            if not isinstance(strategy, dict):
                self.logger.error(f"Invalid strategy type: {type(strategy)}, expected dict")
                return
                
            strategy_key = f"strategy_engine:composed_strategy:{strategy['name']}"
            
            # Store with proper JSON serialization
            import json
            try:
                self.redis_conn.set(strategy_key, json.dumps(strategy), ex=604800)
                self.logger.info(f"Stored composed strategy: {strategy['name']}")
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing composed strategy: {e}")
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing composed strategy: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error storing composed strategy: {e}")
            
        except Exception as e:
            self.logger.error(f"Unexpected error in _store_composed_strategy: {e}")

    def _record_composition(self, success: bool, duration: float):
        """Record composition attempt."""
        try:
            self.composition_stats["compositions_triggered"] += 1
            self.composition_stats["last_composition"] = time.time()
            
            # Store stats in Redis with proper JSON serialization
            try:
                import json
                stats_key = f"strategy_engine:composer:stats:{int(time.time())}"
                self.redis_conn.set(stats_key, json.dumps(self.composition_stats), ex=3600)
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing composition stats: {e}")
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing composition stats: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error storing composition stats: {e}")
            
        except Exception as e:
            self.logger.error(f"Unexpected error recording composition: {e}")

    async def _learn_from_composition(self, strategy: Dict[str, Any], 
                                    market_analysis: Dict[str, Any], duration: float):
        """Learn from successful strategy composition."""
        try:
            if not self.learner:
                return
            
            # Create learning data
            learning_features = [
                duration,
                len(strategy.get("parameters", {})),
                len(market_analysis),
                time.time()
            ]
            
            learning_data = {
                "agent_name": "strategy_engine",
                "learning_type": LearningType.STRATEGY_ADAPTATION,
                "input_features": learning_features,
                "target_value": 1.0,  # Success
                "metadata": {
                    "strategy_name": strategy.get("name", "Unknown"),
                    "strategy_type": strategy.get("type", "Unknown"),
                    "composition_duration": duration
                }
            }
            
            # Learn from composition
            self.learner.learn(learning_data)
            self.logger.info(f"Learned from strategy composition: {strategy.get('name', 'Unknown')}")
            
        except Exception as e:
            self.logger.error(f"Error learning from composition: {e}")

    # Helper methods for Redis data retrieval
    async def _get_current_market_regime(self) -> Optional[str]:
        """Get current market regime from Redis."""
        try:
            regime_key = "market_conditions:current_regime"
            regime = self.redis_conn.get(regime_key)
            
            if regime:
                # Handle both string and bytes responses from Redis
                if isinstance(regime, bytes):
                    regime = regime.decode('utf-8')
                elif not isinstance(regime, str):
                    self.logger.warning(f"Invalid regime data type: {type(regime)}")
                    return "normal"
                    
                return regime
            else:
                return "normal"
                
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting market regime: {e}")
            return "normal"
        except Exception as e:
            self.logger.error(f"Unexpected error getting market regime: {e}")
            return "normal"

    async def _get_previous_market_regime(self) -> Optional[str]:
        """Get previous market regime from Redis."""
        try:
            regime_key = "market_conditions:previous_regime"
            regime = self.redis_conn.get(regime_key)
            
            if regime:
                # Handle both string and bytes responses from Redis
                if isinstance(regime, bytes):
                    regime = regime.decode('utf-8')
                elif not isinstance(regime, str):
                    self.logger.warning(f"Invalid previous regime data type: {type(regime)}")
                    return "normal"
                    
                return regime
            else:
                return "normal"
                
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting previous market regime: {e}")
            return "normal"
        except Exception as e:
            self.logger.error(f"Unexpected error getting previous market regime: {e}")
            return "normal"

    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from Redis."""
        try:
            metrics_key = "strategy_engine:performance:overall"
            metrics = self.redis_conn.get(metrics_key)
            
            if metrics:
                import json
                try:
                    # Handle both string and bytes responses from Redis
                    if isinstance(metrics, bytes):
                        metrics = metrics.decode('utf-8')
                    elif not isinstance(metrics, str):
                        self.logger.warning(f"Invalid metrics data type: {type(metrics)}")
                        return {}
                        
                    parsed_metrics = json.loads(metrics)
                    if isinstance(parsed_metrics, dict):
                        return parsed_metrics
                    else:
                        self.logger.warning(f"Invalid metrics format: expected dict, got {type(parsed_metrics)}")
                        return {}
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for performance metrics: {e}")
                    return {}
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing performance metrics: {e}")
                    return {}
            else:
                return {}
                
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting performance metrics: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error getting performance metrics: {e}")
            return {}

    async def _get_current_market_conditions(self) -> Dict[str, Any]:
        """Get current market conditions from Redis."""
        try:
            conditions_key = "market_conditions:current"
            conditions = self.redis_conn.get(conditions_key)
            
            if conditions:
                import json
                try:
                    # Handle both string and bytes responses from Redis
                    if isinstance(conditions, bytes):
                        conditions = conditions.decode('utf-8')
                    elif not isinstance(conditions, str):
                        self.logger.warning(f"Invalid conditions data type: {type(conditions)}")
                        return {}
                        
                    parsed_conditions = json.loads(conditions)
                    if isinstance(parsed_conditions, dict):
                        return parsed_conditions
                    else:
                        self.logger.warning(f"Invalid conditions format: expected dict, got {type(parsed_conditions)}")
                        return {}
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for market conditions: {e}")
                    return {}
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing market conditions: {e}")
                    return {}
            else:
                return {}
                
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting market conditions: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error getting market conditions: {e}")
            return {}

    async def _get_strategy_coverage(self) -> List[str]:
        """Get current strategy coverage from Redis."""
        try:
            coverage_key = "strategy_engine:coverage:current"
            coverage = self.redis_conn.get(coverage_key)
            
            if coverage:
                import json
                try:
                    # Handle both string and bytes responses from Redis
                    if isinstance(coverage, bytes):
                        coverage = coverage.decode('utf-8')
                    elif not isinstance(coverage, str):
                        self.logger.warning(f"Invalid coverage data type: {type(coverage)}")
                        return []
                        
                    parsed_coverage = json.loads(coverage)
                    if isinstance(parsed_coverage, list):
                        return parsed_coverage
                    else:
                        self.logger.warning(f"Invalid coverage format: expected list, got {type(parsed_coverage)}")
                        return []
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for strategy coverage: {e}")
                    return []
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing strategy coverage: {e}")
                    return []
            else:
                return []
                
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting strategy coverage: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error getting strategy coverage: {e}")
            return []

    async def _get_current_strategies(self) -> List[str]:
        """Get current active strategies from Redis."""
        try:
            strategies_key = "strategy_engine:active_strategies"
            strategies = self.redis_conn.get(strategies_key)
            
            if strategies:
                import json
                try:
                    # Handle both string and bytes responses from Redis
                    if isinstance(strategies, bytes):
                        strategies = strategies.decode('utf-8')
                    elif not isinstance(strategies, str):
                        self.logger.warning(f"Invalid strategies data type: {type(strategies)}")
                        return []
                        
                    parsed_strategies = json.loads(strategies)
                    if isinstance(parsed_strategies, list):
                        return parsed_strategies
                    else:
                        self.logger.warning(f"Invalid strategies format: expected list, got {type(parsed_strategies)}")
                        return []
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for current strategies: {e}")
                    return []
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing current strategies: {e}")
                    return []
            else:
                return []
                
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting current strategies: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error getting current strategies: {e}")
            return []

    # Additional helper methods
    def _calculate_regime_change_score(self, current: str, previous: str) -> float:
        """Calculate regime change score."""
        if current == previous:
            return 0.0
        return 0.8  # Significant change

    def _calculate_overall_performance(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall performance score."""
        try:
            if not metrics:
                return 0.5
            
            # Simple average of available metrics
            scores = []
            for key, value in metrics.items():
                if isinstance(value, (int, float)) and 0 <= value <= 1:
                    scores.append(value)
            
            return sum(scores) / len(scores) if scores else 0.5
            
        except Exception as e:
            self.logger.error(f"Error calculating overall performance: {e}")
            return 0.5

    def _calculate_coverage_gap(self, conditions: Dict[str, Any], coverage: List[str]) -> float:
        """Calculate coverage gap score."""
        try:
            if not conditions or not coverage:
                return 0.5
            
            # Simple gap calculation
            required_coverage = len(conditions) * 0.8  # 80% coverage target
            actual_coverage = len(coverage)
            
            gap = max(0, required_coverage - actual_coverage) / required_coverage
            return gap
            
        except Exception as e:
            self.logger.error(f"Error calculating coverage gap: {e}")
            return 0.5

    def _get_required_strategies(self, market_analysis: Dict[str, Any]) -> List[str]:
        """Get required strategies based on market analysis."""
        try:
            required = []
            
            if market_analysis.get("volatility_level") == "high":
                required.extend(["volatility_trading", "risk_management"])
            
            if market_analysis.get("trend_strength") == "strong":
                required.extend(["trend_following", "momentum_trading"])
            
            if market_analysis.get("market_regime") == "volatile":
                required.extend(["mean_reversion", "arbitrage"])
            
            return list(set(required))  # Remove duplicates
            
        except Exception as e:
            self.logger.error(f"Error getting required strategies: {e}")
            return []

    async def _identify_performance_gaps(self) -> List[str]:
        """Identify performance gaps in current strategies."""
        try:
            gaps = []
            
            # Get performance data for each strategy type
            strategy_types = ["trend_following", "mean_reversion", "arbitrage", "market_making"]
            
            for strategy_type in strategy_types:
                performance = await self._get_strategy_performance(strategy_type)
                if performance and performance.get("score", 0) < 0.5:
                    gaps.append(f"improve_{strategy_type}")
            
            return gaps
            
        except Exception as e:
            self.logger.error(f"Error identifying performance gaps: {e}")
            return []

    async def _get_strategy_performance(self, strategy_type: str) -> Optional[Dict[str, Any]]:
        """Get performance for a specific strategy type."""
        try:
            if not isinstance(strategy_type, str):
                self.logger.error(f"Invalid strategy_type: {type(strategy_type)}, expected string")
                return None
                
            performance_key = f"strategy_engine:performance:{strategy_type}"
            performance = self.redis_conn.get(performance_key)
            
            if performance:
                import json
                try:
                    # Handle both string and bytes responses from Redis
                    if isinstance(performance, bytes):
                        performance = performance.decode('utf-8')
                    elif not isinstance(performance, str):
                        self.logger.warning(f"Invalid performance data type: {type(performance)}")
                        return None
                        
                    parsed_performance = json.loads(performance)
                    if isinstance(parsed_performance, dict):
                        return parsed_performance
                    else:
                        self.logger.warning(f"Invalid performance format: expected dict, got {type(parsed_performance)}")
                        return None
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for strategy performance: {e}")
                    return None
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing strategy performance: {e}")
                    return None
            else:
                return None
                
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting strategy performance: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error getting strategy performance: {e}")
            return None

    def _select_critical_gap(self, gaps: List[str], market_analysis: Dict[str, Any]) -> str:
        """Select the most critical gap to address."""
        try:
            if not gaps:
                return "adaptive"
            
            # Priority order
            priority_order = [
                "risk_management",
                "volatility_trading",
                "trend_following",
                "mean_reversion",
                "arbitrage",
                "market_making"
            ]
            
            # Find highest priority gap
            for priority in priority_order:
                for gap in gaps:
                    if priority in gap:
                        return gap
            
            # Return first gap if no priority match
            return gaps[0]
            
        except Exception as e:
            self.logger.error(f"Error selecting critical gap: {e}")
            return gaps[0] if gaps else "adaptive"

    def _get_active_triggers(self) -> List[str]:
        """Get list of active composition triggers."""
        return [trigger for trigger, active in self.composition_triggers.items() if active]

    # Additional helper methods for market analysis
    async def _get_volatility_level(self) -> str:
        """Get current volatility level."""
        try:
            vol_key = "market_conditions:volatility_level"
            level = self.redis_conn.get(vol_key)
            
            if level:
                # Handle both string and bytes responses from Redis
                if isinstance(level, bytes):
                    level = level.decode('utf-8')
                elif not isinstance(level, str):
                    self.logger.warning(f"Invalid volatility level data type: {type(level)}")
                    return "normal"
                    
                return level
            else:
                return "normal"
                
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting volatility level: {e}")
            return "normal"
        except Exception as e:
            self.logger.error(f"Unexpected error getting volatility level: {e}")
            return "normal"

    async def _get_trend_strength(self) -> str:
        """Get current trend strength."""
        try:
            trend_key = "market_conditions:trend_strength"
            strength = self.redis_conn.get(trend_key)
            
            if strength:
                # Handle both string and bytes responses from Redis
                if isinstance(strength, bytes):
                    strength = strength.decode('utf-8')
                elif not isinstance(strength, str):
                    self.logger.warning(f"Invalid trend strength data type: {type(strength)}")
                    return "weak"
                    
                return strength
            else:
                return "weak"
                
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting trend strength: {e}")
            return "weak"
        except Exception as e:
            self.logger.error(f"Unexpected error getting trend strength: {e}")
            return "weak"

    async def _get_volume_profile(self) -> Dict[str, Any]:
        """Get current volume profile."""
        try:
            volume_key = "market_conditions:volume_profile"
            profile = self.redis_conn.get(volume_key)
            
            if profile:
                import json
                try:
                    # Handle both string and bytes responses from Redis
                    if isinstance(profile, bytes):
                        profile = profile.decode('utf-8')
                    elif not isinstance(profile, str):
                        self.logger.warning(f"Invalid volume profile data type: {type(profile)}")
                        return {}
                        
                    parsed_profile = json.loads(profile)
                    if isinstance(parsed_profile, dict):
                        return parsed_profile
                    else:
                        self.logger.warning(f"Invalid volume profile format: expected dict, got {type(parsed_profile)}")
                        return {}
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for volume profile: {e}")
                    return {}
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing volume profile: {e}")
                    return {}
            else:
                return {}
                
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting volume profile: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error getting volume profile: {e}")
            return {}

    async def _get_correlation_matrix(self) -> Dict[str, Any]:
        """Get current correlation matrix."""
        try:
            corr_key = "market_conditions:correlation_matrix"
            matrix = self.redis_conn.get(corr_key)
            
            if matrix:
                import json
                try:
                    # Handle both string and bytes responses from Redis
                    if isinstance(matrix, bytes):
                        matrix = matrix.decode('utf-8')
                    elif not isinstance(matrix, str):
                        self.logger.warning(f"Invalid correlation matrix data type: {type(matrix)}")
                        return {}
                        
                    parsed_matrix = json.loads(matrix)
                    if isinstance(parsed_matrix, dict):
                        return parsed_matrix
                    else:
                        self.logger.warning(f"Invalid correlation matrix format: expected dict, got {type(parsed_matrix)}")
                        return {}
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for correlation matrix: {e}")
                    return {}
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing correlation matrix: {e}")
                    return {}
            else:
                return {}
                
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting correlation matrix: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error getting correlation matrix: {e}")
            return {}

    async def _get_risk_metrics(self) -> Dict[str, Any]:
        """Get current risk metrics."""
        try:
            risk_key = "market_conditions:risk_metrics"
            metrics = self.redis_conn.get(risk_key)
            
            if metrics:
                import json
                try:
                    # Handle both string and bytes responses from Redis
                    if isinstance(metrics, bytes):
                        metrics = metrics.decode('utf-8')
                    elif not isinstance(metrics, str):
                        self.logger.warning(f"Invalid risk metrics data type: {type(metrics)}")
                        return {}
                        
                    parsed_metrics = json.loads(metrics)
                    if isinstance(parsed_metrics, dict):
                        return parsed_metrics
                    else:
                        self.logger.warning(f"Invalid risk metrics format: expected dict, got {type(parsed_metrics)}")
                        return {}
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for risk metrics: {e}")
                    return {}
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing risk metrics: {e}")
                    return {}
            else:
                return {}
                
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting risk metrics: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Unexpected error getting risk metrics: {e}")
            return {}

    def get_composition_stats(self) -> Dict[str, Any]:
        """Get composition statistics."""
        return {
            **self.composition_stats,
            "active_triggers": self._get_active_triggers()
        }

    def force_composition(self):
        """Force immediate strategy composition."""
        try:
            self.composition_triggers["forced_composition"] = True
            self.logger.info("Forced composition triggered")
        except Exception as e:
            self.logger.error(f"Error forcing composition: {e}")
