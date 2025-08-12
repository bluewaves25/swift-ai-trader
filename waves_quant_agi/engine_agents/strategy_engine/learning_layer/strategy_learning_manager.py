#!/usr/bin/env python3
"""
Strategy Learning Manager
Comprehensive learning system for strategy engine optimization.
"""

import asyncio
import time
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from engine_agents.shared_utils import get_shared_logger, get_shared_redis

class StrategyLearningManager:
    """Manages learning and optimization for all strategy components."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "learning_manager")
        self.redis_conn = get_shared_redis()
        
        # Learning configuration
        self.learning_rate = config.get("learning_rate", 0.01)
        self.batch_size = config.get("batch_size", 32)
        self.max_history = config.get("max_history", 1000)
        self.performance_threshold = config.get("performance_threshold", 0.6)
        
        # Learning state
        self.learning_history: List[Dict[str, Any]] = []
        self.performance_history: List[Dict[str, Any]] = []
        self.optimization_history: List[Dict[str, Any]] = []
        
        # Strategy performance tracking
        self.strategy_performance: Dict[str, Dict[str, Any]] = {}
        self.parameter_optimization: Dict[str, Dict[str, Any]] = {}
        
        # Learning statistics
        self.stats = {
            "learning_cycles": 0,
            "optimizations_performed": 0,
            "strategies_improved": 0,
            "learning_errors": 0,
            "start_time": time.time()
        }

    async def learn_from_strategy_execution(self, strategy_data: Dict[str, Any], 
                                          execution_result: Dict[str, Any]) -> bool:
        """Learn from strategy execution results."""
        try:
            strategy_name = strategy_data.get("name", "unknown")
            strategy_type = strategy_data.get("type", "unknown")
            
            # Create learning record
            learning_record = {
                "strategy_name": strategy_name,
                "strategy_type": strategy_type,
                "execution_data": execution_result,
                "timestamp": int(time.time()),
                "learning_type": "execution_feedback"
            }
            
            # Add to learning history
            self.learning_history.append(learning_record)
            
            # Limit history size
            if len(self.learning_history) > self.max_history:
                self.learning_history = self.learning_history[-self.max_history:]
            
            # Update strategy performance
            await self._update_strategy_performance(strategy_name, execution_result)
            
            # Check if optimization is needed
            if await self._should_optimize_strategy(strategy_name):
                await self._optimize_strategy(strategy_name)
            
            self.stats["learning_cycles"] += 1
            self.logger.info(f"Learned from {strategy_name} execution")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error learning from strategy execution: {e}")
            self.stats["learning_errors"] += 1
            return False

    async def learn_from_market_conditions(self, market_data: Dict[str, Any], 
                                         strategy_performance: Dict[str, Any]) -> bool:
        """Learn from market conditions and strategy performance."""
        try:
            # Analyze market conditions
            market_analysis = await self._analyze_market_conditions(market_data)
            
            # Create learning record
            learning_record = {
                "market_analysis": market_analysis,
                "strategy_performance": strategy_performance,
                "timestamp": int(time.time()),
                "learning_type": "market_conditions"
            }
            
            # Add to learning history
            self.learning_history.append(learning_record)
            
            # Limit history size
            if len(self.learning_history) > self.max_history:
                self.learning_history = self.learning_history[-self.max_history:]
            
            # Update performance history
            self.performance_history.append({
                "timestamp": int(time.time()),
                "market_conditions": market_analysis,
                "overall_performance": self._calculate_overall_performance(strategy_performance)
            })
            
            # Check for regime changes
            if await self._detect_regime_change(market_analysis):
                await self._handle_regime_change(market_analysis)
            
            self.logger.info("Learned from market conditions")
            return True
            
        except Exception as e:
            self.logger.error(f"Error learning from market conditions: {e}")
            self.stats["learning_errors"] += 1
            return False

    async def _analyze_market_conditions(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market conditions for learning."""
        try:
            analysis = {
                "volatility": self._calculate_volatility(market_data),
                "trend_strength": self._calculate_trend_strength(market_data),
                "volume_profile": self._calculate_volume_profile(market_data),
                "correlation": self._calculate_correlation(market_data),
                "regime": self._determine_market_regime(market_data)
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing market conditions: {e}")
            return {}

    def _calculate_volatility(self, market_data: Dict[str, Any]) -> float:
        """Calculate market volatility."""
        try:
            if not market_data or "prices" not in market_data:
                return 0.0
            
            prices = market_data["prices"]
            if len(prices) < 2:
                return 0.0
            
            returns = np.diff(np.log(prices))
            return float(np.std(returns))
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility: {e}")
            return 0.0

    def _calculate_trend_strength(self, market_data: Dict[str, Any]) -> float:
        """Calculate trend strength."""
        try:
            if not market_data or "prices" not in market_data:
                return 0.0
            
            prices = market_data["prices"]
            if len(prices) < 20:
                return 0.0
            
            # Simple trend calculation
            short_ma = np.mean(prices[-10:])
            long_ma = np.mean(prices[-20:])
            
            if long_ma == 0:
                return 0.0
            
            trend_strength = (short_ma - long_ma) / long_ma
            return float(abs(trend_strength))
            
        except Exception as e:
            self.logger.error(f"Error calculating trend strength: {e}")
            return 0.0

    def _calculate_volume_profile(self, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate volume profile."""
        try:
            if not market_data or "volumes" not in market_data:
                return {"avg_volume": 0.0, "volume_trend": 0.0}
            
            volumes = market_data["volumes"]
            if len(volumes) < 2:
                return {"avg_volume": 0.0, "volume_trend": 0.0}
            
            avg_volume = np.mean(volumes)
            volume_trend = (volumes[-1] - volumes[0]) / volumes[0] if volumes[0] > 0 else 0.0
            
            return {
                "avg_volume": float(avg_volume),
                "volume_trend": float(volume_trend)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating volume profile: {e}")
            return {"avg_volume": 0.0, "volume_trend": 0.0}

    def _calculate_correlation(self, market_data: Dict[str, Any]) -> float:
        """Calculate market correlation."""
        try:
            if not market_data or "correlations" not in market_data:
                return 0.0
            
            correlations = market_data["correlations"]
            if not correlations:
                return 0.0
            
            return float(np.mean(correlations))
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation: {e}")
            return 0.0

    def _determine_market_regime(self, market_data: Dict[str, Any]) -> str:
        """Determine current market regime."""
        try:
            volatility = self._calculate_volatility(market_data)
            trend_strength = self._calculate_trend_strength(market_data)
            
            if volatility > 0.05 and trend_strength > 0.1:
                return "trending"
            elif volatility > 0.05 and trend_strength < 0.05:
                return "volatile"
            elif volatility < 0.02 and trend_strength < 0.05:
                return "sideways"
            else:
                return "normal"
                
        except Exception as e:
            self.logger.error(f"Error determining market regime: {e}")
            return "normal"

    async def _update_strategy_performance(self, strategy_name: str, execution_result: Dict[str, Any]):
        """Update strategy performance tracking."""
        try:
            if strategy_name not in self.strategy_performance:
                self.strategy_performance[strategy_name] = {
                    "executions": 0,
                    "successful_executions": 0,
                    "total_pnl": 0.0,
                    "avg_pnl": 0.0,
                    "success_rate": 0.0,
                    "last_execution": 0
                }
            
            performance = self.strategy_performance[strategy_name]
            performance["executions"] += 1
            performance["last_execution"] = int(time.time())
            
            # Update PnL
            pnl = execution_result.get("pnl", 0.0)
            performance["total_pnl"] += pnl
            performance["avg_pnl"] = performance["total_pnl"] / performance["executions"]
            
            # Update success rate
            if execution_result.get("success", False):
                performance["successful_executions"] += 1
            
            performance["success_rate"] = performance["successful_executions"] / performance["executions"]
            
            # Store performance data in Redis with proper JSON serialization
            try:
                import json
                performance_key = f"strategy_engine:learning:performance:{strategy_name}"
                self.redis_conn.set(performance_key, json.dumps(performance), ex=604800)
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing performance: {e}")
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing performance: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error storing performance: {e}")
            
        except Exception as e:
            self.logger.error(f"Error updating strategy performance: {e}")

    async def _should_optimize_strategy(self, strategy_name: str) -> bool:
        """Check if strategy should be optimized."""
        try:
            if strategy_name not in self.strategy_performance:
                return False
            
            performance = self.strategy_performance[strategy_name]
            
            # Optimize if success rate is low
            if performance["success_rate"] < self.performance_threshold:
                return True
            
            # Optimize if average PnL is negative
            if performance["avg_pnl"] < 0:
                return True
            
            # Optimize if not optimized recently
            last_optimization = self.parameter_optimization.get(strategy_name, {}).get("last_optimization", 0)
            if time.time() - last_optimization > 3600:  # 1 hour
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking optimization need: {e}")
            return False

    async def _optimize_strategy(self, strategy_name: str):
        """Optimize strategy parameters."""
        try:
            self.logger.info(f"Optimizing strategy: {strategy_name}")
            
            # Get current performance
            performance = self.strategy_performance.get(strategy_name, {})
            
            # Get current parameters
            current_params = await self._get_strategy_parameters(strategy_name)
            
            # Generate optimized parameters
            optimized_params = await self._generate_optimized_parameters(
                strategy_name, current_params, performance
            )
            
            if optimized_params:
                # Store optimization
                optimization_record = {
                    "strategy_name": strategy_name,
                    "previous_params": current_params,
                    "optimized_params": optimized_params,
                    "performance_improvement": self._calculate_improvement(current_params, optimized_params),
                    "timestamp": int(time.time())
                }
                
                self.parameter_optimization[strategy_name] = optimization_record
                self.optimization_history.append(optimization_record)
                
                # Apply optimized parameters
                await self._apply_optimized_parameters(strategy_name, optimized_params)
                
                self.stats["optimizations_performed"] += 1
                self.stats["strategies_improved"] += 1
                
                self.logger.info(f"Strategy {strategy_name} optimized successfully")
            
        except Exception as e:
            self.logger.error(f"Error optimizing strategy {strategy_name}: {e}")

    async def _get_strategy_parameters(self, strategy_name: str) -> Dict[str, Any]:
        """Get current strategy parameters."""
        try:
            params_key = f"strategy_engine:parameters:{strategy_name}"
            params = self.redis_conn.get(params_key)
            
            if params:
                import json
                return json.loads(params)
            
            # Return default parameters
            return {
                "confidence_threshold": 0.6,
                "risk_tolerance": 0.5,
                "position_size": 0.1
            }
            
        except Exception as e:
            self.logger.error(f"Error getting strategy parameters: {e}")
            return {}

    async def _generate_optimized_parameters(self, strategy_name: str, 
                                          current_params: Dict[str, Any], 
                                          performance: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate optimized parameters for strategy."""
        try:
            # Simple parameter optimization based on performance
            optimized_params = current_params.copy()
            
            # Adjust confidence threshold based on success rate
            success_rate = performance.get("success_rate", 0.5)
            if success_rate < 0.4:
                optimized_params["confidence_threshold"] = min(0.9, current_params.get("confidence_threshold", 0.6) + 0.1)
            elif success_rate > 0.8:
                optimized_params["confidence_threshold"] = max(0.3, current_params.get("confidence_threshold", 0.6) - 0.05)
            
            # Adjust risk tolerance based on PnL
            avg_pnl = performance.get("avg_pnl", 0.0)
            if avg_pnl < 0:
                optimized_params["risk_tolerance"] = max(0.1, current_params.get("risk_tolerance", 0.5) - 0.1)
            elif avg_pnl > 0.01:
                optimized_params["risk_tolerance"] = min(0.9, current_params.get("risk_tolerance", 0.5) + 0.05)
            
            # Adjust position size based on volatility
            if performance.get("volatility", 0.0) > 0.05:
                optimized_params["position_size"] = max(0.05, current_params.get("position_size", 0.1) - 0.02)
            else:
                optimized_params["position_size"] = min(0.2, current_params.get("position_size", 0.1) + 0.02)
            
            return optimized_params
            
        except Exception as e:
            self.logger.error(f"Error generating optimized parameters: {e}")
            return None

    def _calculate_improvement(self, current_params: Dict[str, Any], 
                             optimized_params: Dict[str, Any]) -> float:
        """Calculate expected improvement from parameter optimization."""
        try:
            improvement = 0.0
            
            for param in current_params:
                if param in optimized_params:
                    current_val = current_params[param]
                    optimized_val = optimized_params[param]
                    
                    if isinstance(current_val, (int, float)) and isinstance(optimized_val, (int, float)):
                        if current_val != 0:
                            change = abs(optimized_val - current_val) / abs(current_val)
                            improvement += change
            
            return improvement / len(current_params) if current_params else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating improvement: {e}")
            return 0.0

    async def _apply_optimized_parameters(self, strategy_name: str, optimized_params: Dict[str, Any]):
        """Apply optimized parameters to strategy."""
        try:
            # Store optimized parameters in Redis with proper JSON serialization
            try:
                import json
                params_key = f"strategy_engine:learning:optimized_params:{strategy_name}"
                self.redis_conn.set(params_key, json.dumps(optimized_params), ex=604800)
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing optimized parameters: {e}")
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing optimized parameters: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error storing optimized parameters: {e}")
            
            # Notify strategy engine of parameter update
            update_notification = {
                "type": "parameter_update",
                "strategy_name": strategy_name,
                "new_parameters": optimized_params,
                "timestamp": int(time.time())
            }
            
            self.redis_conn.publish("strategy_engine:parameter_updates", str(update_notification))
            
            self.logger.info(f"Applied optimized parameters for {strategy_name}")
            
        except Exception as e:
            self.logger.error(f"Error applying optimized parameters: {e}")

    async def _detect_regime_change(self, market_analysis: Dict[str, Any]) -> bool:
        """Detect if market regime has changed."""
        try:
            # Get previous market regime
            previous_regime = await self._get_previous_market_regime()
            current_regime = market_analysis.get("regime", "normal")
            
            if previous_regime and previous_regime != current_regime:
                # Store new regime
                await self._store_market_regime(current_regime)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error detecting regime change: {e}")
            return False

    async def _handle_regime_change(self, market_analysis: Dict[str, Any]):
        """Handle market regime change."""
        try:
            new_regime = market_analysis.get("regime", "normal")
            self.logger.info(f"Market regime changed to: {new_regime}")
            
            # Trigger strategy adaptation
            adaptation_notification = {
                "type": "regime_change",
                "new_regime": new_regime,
                "market_analysis": market_analysis,
                "timestamp": int(time.time())
            }
            
            self.redis_conn.publish("strategy_engine:regime_changes", str(adaptation_notification))
            
            # Update learning parameters for new regime
            await self._adapt_to_new_regime(new_regime)
            
            # Store regime change data in Redis with proper JSON serialization
            try:
                import json
                regime_data = {
                    "previous_regime": previous_regime,
                    "new_regime": new_regime,
                    "change_timestamp": int(time.time()),
                    "market_conditions": market_analysis
                }
                
                self.redis_conn.set(
                    f"strategy_engine:learning:regime_change:{int(time.time())}", 
                    json.dumps(regime_data), 
                    ex=604800
                )
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing regime change: {e}")
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing regime change: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error storing regime change: {e}")
            
        except Exception as e:
            self.logger.error(f"Error handling regime change: {e}")

    async def _adapt_to_new_regime(self, new_regime: str):
        """Adapt learning parameters to new market regime."""
        try:
            # Adjust learning rate based on regime
            if new_regime == "volatile":
                self.learning_rate = min(0.02, self.learning_rate * 1.5)
            elif new_regime == "trending":
                self.learning_rate = min(0.015, self.learning_rate * 1.2)
            elif new_regime == "sideways":
                self.learning_rate = max(0.005, self.learning_rate * 0.8)
            
            # Store adapted parameters
            adaptation_record = {
                "regime": new_regime,
                "learning_rate": self.learning_rate,
                "timestamp": int(time.time())
            }
            
            self.redis_conn.set(
                f"strategy_engine:learning:regime_adaptation:{new_regime}", 
                str(adaptation_record), 
                ex=604800
            )
            
            self.logger.info(f"Adapted to new regime: {new_regime}")
            
        except Exception as e:
            self.logger.error(f"Error adapting to new regime: {e}")

    async def _get_previous_market_regime(self) -> Optional[str]:
        """Get previous market regime from Redis."""
        try:
            previous_key = "strategy_engine:learning:previous_regime"
            previous_regime = self.redis_conn.get(previous_key)
            
            if previous_regime:
                import json
                try:
                    # Handle both string and bytes responses from Redis
                    if isinstance(previous_regime, bytes):
                        previous_regime = previous_regime.decode('utf-8')
                    elif not isinstance(previous_regime, str):
                        return None
                        
                    parsed_regime = json.loads(previous_regime)
                    if isinstance(parsed_regime, str):
                        return parsed_regime
                    else:
                        return None
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for previous market regime: {e}")
                    return None
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing previous market regime: {e}")
                    return None
            
            return None
            
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting previous market regime: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error getting previous market regime: {e}")
            return None

    async def _store_market_regime(self, regime: str):
        """Store current market regime."""
        try:
            if not isinstance(regime, str):
                self.logger.error(f"Invalid regime type: {type(regime)}, expected string")
                return
                
            # Store previous regime first
            try:
                import json
                current_key = "strategy_engine:learning:current_regime"
                previous_key = "strategy_engine:learning:previous_regime"
                
                current_regime = self.redis_conn.get(current_key)
                if current_regime:
                    # Handle bytes response from Redis
                    if isinstance(current_regime, bytes):
                        current_regime = current_regime.decode('utf-8')
                    elif isinstance(current_regime, str):
                        try:
                            parsed_regime = json.loads(current_regime)
                            if isinstance(parsed_regime, str):
                                current_regime = parsed_regime
                            else:
                                current_regime = "unknown"
                        except json.JSONDecodeError:
                            current_regime = "unknown"
                    else:
                        current_regime = "unknown"
                        
                    # Store previous regime
                    self.redis_conn.set(previous_key, json.dumps(current_regime), ex=604800)
                
                # Store current regime
                self.redis_conn.set(current_key, json.dumps(regime), ex=604800)
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing market regime: {e}")
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing market regime: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error storing market regime: {e}")
                
        except Exception as e:
            self.logger.error(f"Unexpected error in _store_market_regime: {e}")

    def _calculate_overall_performance(self, strategy_performance: Dict[str, Any]) -> float:
        """Calculate overall strategy performance."""
        try:
            if not strategy_performance:
                return 0.0
            
            # Simple average of performance metrics
            metrics = []
            for strategy, perf in strategy_performance.items():
                if isinstance(perf, dict):
                    success_rate = perf.get("success_rate", 0.5)
                    avg_pnl = perf.get("avg_pnl", 0.0)
                    
                    # Normalize PnL to 0-1 range
                    normalized_pnl = max(0, min(1, (avg_pnl + 0.1) / 0.2))
                    
                    # Combined score
                    combined_score = (success_rate + normalized_pnl) / 2
                    metrics.append(combined_score)
            
            return np.mean(metrics) if metrics else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating overall performance: {e}")
            return 0.0

    async def get_learning_insights(self) -> Dict[str, Any]:
        """Get insights from learning data."""
        try:
            insights = {
                "total_learning_cycles": self.stats["learning_cycles"],
                "optimizations_performed": self.stats["optimizations_performed"],
                "strategies_improved": self.stats["strategies_improved"],
                "current_market_regime": await self._get_previous_market_regime(),
                "strategy_performance_summary": {},
                "recent_optimizations": self.optimization_history[-5:] if self.optimization_history else [],
                "learning_rate": self.learning_rate,
                "uptime": time.time() - self.stats["start_time"]
            }
            
            # Add strategy performance summary
            for strategy_name, performance in self.strategy_performance.items():
                insights["strategy_performance_summary"][strategy_name] = {
                    "success_rate": performance.get("success_rate", 0.0),
                    "avg_pnl": performance.get("avg_pnl", 0.0),
                    "executions": performance.get("executions", 0)
                }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error getting learning insights: {e}")
            return {"error": str(e)}

    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics."""
        return {
            **self.stats,
            "learning_history_size": len(self.learning_history),
            "performance_history_size": len(self.performance_history),
            "optimization_history_size": len(self.optimization_history),
            "active_strategies": len(self.strategy_performance)
        }

    async def reset_learning(self):
        """Reset learning state."""
        try:
            self.learning_history.clear()
            self.performance_history.clear()
            self.optimization_history.clear()
            self.strategy_performance.clear()
            self.parameter_optimization.clear()
            
            # Reset stats
            self.stats = {
                "learning_cycles": 0,
                "optimizations_performed": 0,
                "strategies_improved": 0,
                "learning_errors": 0,
                "start_time": time.time()
            }
            
            self.logger.info("Learning state reset")
            
        except Exception as e:
            self.logger.error(f"Error resetting learning: {e}")

    async def export_learning_data(self) -> Dict[str, Any]:
        """Export learning data for analysis."""
        try:
            export_data = {
                "learning_history": self.learning_history,
                "performance_history": self.performance_history,
                "optimization_history": self.optimization_history,
                "strategy_performance": self.strategy_performance,
                "parameter_optimization": self.parameter_optimization,
                "stats": self.stats,
                "export_timestamp": int(time.time())
            }
            
            # Store export data in Redis with proper JSON serialization
            try:
                import json
                export_key = f"strategy_engine:learning:export:{int(time.time())}"
                self.redis_conn.set(export_key, json.dumps(export_data), ex=86400)  # 24 hours
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing export data: {e}")
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing export data: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error storing export data: {e}")
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Error exporting learning data: {e}")
            return {"error": str(e)}
