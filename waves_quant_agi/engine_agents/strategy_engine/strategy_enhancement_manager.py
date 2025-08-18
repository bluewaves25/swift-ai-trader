#!/usr/bin/env python3
"""
Strategy Enhancement Manager
Comprehensive integration of all strategy-specific features:
1. Config Loading: Strategy-specific parameters
2. Signal Generation: Strategy-specific SL/TP
3. Rate Limiting: Strategy-specific trade limits
4. Execution: Strategy-specific execution paths
5. Monitoring: Strategy-specific performance tracking
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from .configs.strategy_configs import (
    get_strategy_config, 
    get_all_strategy_configs,
    get_session_config, 
    get_current_session
)
from .risk_management.sltp_calculators.strategy_sltp_calculator import StrategySLTPCalculator
from .risk_management.rate_limiting.rate_limiter import RateLimiter
from .risk_management.signal_quality.signal_quality_assessor import SignalQualityAssessor
from .execution.session_management.session_manager import SessionManager

# Learning and Composing Components
from .strategies.composers.ml_composer import MLComposer
from .strategies.composers.online_generator import OnlineGenerator
from .learning.strategy_learning_manager import StrategyLearningManager
from .learning.strategy_adaptation_engine import StrategyAdaptationEngine

class StrategyEnhancementManager:
    """Comprehensive Strategy Enhancement Manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = None
        
        # Core components
        self.sltp_calculator = StrategySLTPCalculator()
        self.rate_limiter = RateLimiter(config)
        self.signal_quality_assessor = SignalQualityAssessor(config)
        self.session_manager = SessionManager(config)
        
        # Learning and Composing Components
        self.ml_composer = MLComposer(config)
        self.online_generator = OnlineGenerator(config)
        self.strategy_learning_manager = StrategyLearningManager(config)
        self.strategy_adaptation_engine = StrategyAdaptationEngine(config)
        
        # Strategy state tracking
        self.strategy_performance = {}
        self.total_signals_processed = 0
        self.signals_accepted = 0
        self.signals_rejected = 0
        
        # Initialize strategy performance tracking
        self._initialize_strategy_tracking()
        
        # Initialize learning and composing components
        self._initialize_learning_components()
    
    async def _initialize_learning_components(self):
        """Initialize learning and composing components."""
        try:
            # Initialize ML Composer
            await self.ml_composer.initialize()
            
            # Initialize Online Generator
            await self.online_generator.initialize()
            
            # Initialize Strategy Learning Manager
            await self.strategy_learning_manager.initialize()
            
            # Initialize Strategy Adaptation Engine
            await self.strategy_adaptation_engine.initialize()
            
            if self.logger:
                self.logger.info("✅ Learning and composing components initialized successfully")
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error initializing learning components: {e}")
    
    def set_logger(self, logger):
        """Set logger for all components."""
        self.logger = logger
        self.sltp_calculator.set_logger(logger)
        self.rate_limiter.set_logger(logger)
        self.signal_quality_assessor.set_logger(logger)
        self.session_manager.set_logger(logger)
        
        # Set logger for learning and composing components
        self.ml_composer.set_logger(logger)
        self.online_generator.set_logger(logger)
        self.strategy_learning_manager.set_logger(logger)
        self.strategy_adaptation_engine.set_logger(logger)
    
    def _initialize_strategy_tracking(self):
        """Initialize strategy performance tracking."""
        all_configs = get_all_strategy_configs()
        
        for strategy_type in all_configs.keys():
            self.strategy_performance[strategy_type] = {
                "total_signals": 0,
                "accepted_signals": 0,
                "rejected_signals": 0,
                "total_pnl": 0.0,
                "win_rate": 0.0,
                "avg_risk_reward": 0.0,
                "last_update": time.time()
            }
    
    async def process_enhanced_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Process a trading signal with comprehensive strategy-specific enhancements."""
        try:
            start_time = time.time()
            signal_id = signal.get("signal_id", f"signal_{int(time.time() * 1000)}")
            strategy_type = signal.get("strategy_type", "trend_following")
            
            if self.logger:
                self.logger.info(f"🔄 Processing enhanced signal: {signal_id} ({strategy_type})")
            
            # 1. CONFIG LOADING: Load strategy-specific parameters
            strategy_config = get_strategy_config(strategy_type)
            if not strategy_config:
                return self._create_rejection_response(signal_id, "Invalid strategy type")
            
            # 2. RATE LIMITING: Check if we can process this signal
            if not self.rate_limiter.check_rate_limits(
                signal.get("symbol", "unknown"), 
                strategy_type
            ):
                return self._create_rejection_response(signal_id, "Rate limit exceeded")
            
            # 3. SESSION OPTIMIZATION: Check session appropriateness
            session_result = await self._check_session_appropriateness(strategy_type)
            if not session_result["session_appropriate"]:
                return self._create_rejection_response(
                    signal_id, 
                    f"Session inappropriate: {session_result['reason']}"
                )
            
            # 4. SIGNAL GENERATION: Calculate strategy-specific SL/TP
            sltp_result = await self._generate_enhanced_sltp(signal, strategy_config)
            if not sltp_result["success"]:
                return self._create_rejection_response(signal_id, sltp_result["reason"])
            
            # 5. SIGNAL QUALITY ASSESSMENT: Evaluate signal quality
            quality_result = await self._assess_enhanced_signal_quality(signal, sltp_result, strategy_config)
            if not quality_result["success"]:
                return self._create_rejection_response(signal_id, quality_result["reason"])
            
            # 6. EXECUTION ROUTING: Route to appropriate execution path
            execution_result = await self._route_enhanced_execution(
                signal, sltp_result, strategy_config
            )
            
            # 7. MONITORING: Track strategy-specific performance
            await self._track_enhanced_performance(
                signal, execution_result, strategy_config, quality_result
            )
            
            # Update statistics
            self.total_signals_processed += 1
            self.signals_accepted += 1
            
            processing_time = (time.time() - start_time) * 1000
            
            if self.logger:
                self.logger.info(f"✅ Enhanced signal processed successfully in {processing_time:.2f}ms")
            
            return {
                "success": True,
                "signal_id": signal_id,
                "strategy_type": strategy_type,
                "sltp_result": sltp_result,
                "quality_score": quality_result["quality_score"],
                "execution_result": execution_result,
                "processing_time_ms": processing_time,
                "enhancements_applied": [
                    "config_loading",
                    "rate_limiting", 
                    "session_optimization",
                    "enhanced_sltp",
                    "quality_assessment",
                    "execution_routing",
                    "performance_tracking"
                ]
            }
            
        except Exception as e:
            self.total_signals_processed += 1
            self.signals_rejected += 1
            
            if self.logger:
                self.logger.error(f"❌ Error processing enhanced signal: {e}")
            
            return {
                "success": False,
                "reason": f"Processing error: {str(e)}",
                "signal_id": signal.get("signal_id", "unknown")
            }
    
    async def _check_session_appropriateness(self, strategy_type: str) -> Dict[str, Any]:
        """Check if strategy is appropriate for current session."""
        try:
            current_session_info = self.session_manager.get_current_session_info()
            current_session = current_session_info.get("current_session", "unknown")
            
            # Get strategy session preferences
            strategy_config = get_strategy_config(strategy_type)
            session_preferences = strategy_config.get("session_preference", [])
            
            if current_session in session_preferences:
                return {
                    "success": True,
                    "current_session": current_session,
                    "session_appropriate": True,
                    "session_score": 1.0
                }
            
            return {
                "success": True,
                "current_session": current_session,
                "session_appropriate": False,
                "session_score": 0.0,
                "reason": f"Strategy {strategy_type} prefers {session_preferences}, current: {current_session}"
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error checking session appropriateness: {e}")
            return {
                "success": False,
                "reason": f"Session check error: {str(e)}"
            }
    
    async def _generate_enhanced_sltp(
        self, 
        signal: Dict[str, Any], 
        strategy_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate enhanced strategy-specific SL/TP."""
        try:
            strategy_type = signal.get("strategy_type", "trend_following")
            action = signal.get("action", "BUY")
            entry_price = signal.get("entry_price", 0.0)
            bid = signal.get("bid", entry_price)
            ask = signal.get("ask", entry_price)
            volatility = signal.get("volatility", 0.02)
            
            # Calculate SL/TP using strategy-specific calculator
            sltp_result = self.sltp_calculator.calculate_sltp(
                strategy_type=strategy_type,
                action=action,
                entry_price=entry_price,
                bid=bid,
                ask=ask,
                volatility=volatility
            )
            
            return {
                "success": True,
                "sltp_data": sltp_result
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error generating enhanced SL/TP: {e}")
            return {
                "success": False,
                "reason": f"Enhanced SL/TP generation error: {str(e)}"
            }
    
    async def _assess_enhanced_signal_quality(
        self, 
        signal: Dict[str, Any], 
        sltp_result: Dict[str, Any],
        strategy_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess signal quality with enhanced strategy-specific criteria."""
        try:
            # Add SL/TP metadata to signal for quality assessment
            signal["sltp_metadata"] = sltp_result["sltp_data"]
            
            # Get base quality assessment
            quality_result = self.signal_quality_assessor.assess_signal_quality(signal)
            
            # Apply strategy-specific quality enhancements
            strategy_type = signal.get("strategy_type", "trend_following")
            enhanced_quality = await self._apply_strategy_quality_enhancements(
                signal, quality_result, strategy_config
            )
            
            return enhanced_quality
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error assessing enhanced signal quality: {e}")
            return {
                "success": False,
                "reason": f"Enhanced quality assessment error: {str(e)}"
            }
    
    async def _apply_strategy_quality_enhancements(
        self,
        signal: Dict[str, Any],
        base_quality: Dict[str, Any],
        strategy_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply strategy-specific quality enhancements."""
        try:
            strategy_type = signal.get("strategy_type", "trend_following")
            quality_score = base_quality.get("quality_score", 0)
            rejection_reasons = base_quality.get("rejection_reasons", [])
            
            # Strategy-specific quality adjustments
            if strategy_type in ["arbitrage", "market_making"]:
                # HFT strategies need reasonable quality signals (lower threshold due to different criteria)
                if quality_score < 50:  # Lower threshold for HFT
                    rejection_reasons.append(f"HFT strategy quality too low: {quality_score} < 50")
                    return {
                        "success": False,
                        "reason": "HFT quality threshold not met",
                        "quality_score": quality_score
                    }
            
            # Check if we have enough quality to proceed
            if quality_score < 50:
                return {
                    "success": False,
                    "reason": f"Quality score too low: {quality_score} < 50",
                    "quality_score": quality_score,
                    "rejection_reasons": rejection_reasons
                }
            
            return {
                "success": True,
                "quality_score": quality_score,
                "rejection_reasons": rejection_reasons,
                "enhancements_applied": ["strategy_specific_quality"]
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error applying strategy quality enhancements: {e}")
            return base_quality
    
    async def _route_enhanced_execution(
        self, 
        signal: Dict[str, Any], 
        sltp_result: Dict[str, Any], 
        strategy_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route signal to appropriate execution path with enhanced logic."""
        try:
            strategy_type = signal.get("strategy_type", "trend_following")
            
            # Route based on strategy type
            if strategy_type in ["arbitrage", "market_making"]:
                execution_result = await self._execute_hft_strategy(signal, sltp_result)
            else:
                execution_result = await self._execute_standard_strategy(signal, sltp_result)
            
            return execution_result
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error routing enhanced execution: {e}")
            return {
                "success": False,
                "reason": f"Enhanced execution routing error: {str(e)}"
            }
    
    async def _execute_hft_strategy(
        self, 
        signal: Dict[str, Any], 
        sltp_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute HFT strategy with ultra-fast processing."""
        try:
            execution_result = {
                "strategy_type": signal.get("strategy_type"),
                "symbol": signal.get("symbol"),
                "action": signal.get("action"),
                "volume": signal.get("volume", 1.0),
                "sltp_data": sltp_result["sltp_data"],
                "priority": "HIGH",
                "execution_type": "hft",
                "execution_speed": "ultra_fast"
            }
            
            return {
                "success": True,
                "execution_type": "hft",
                "execution_result": execution_result
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error executing HFT strategy: {e}")
            return {
                "success": False,
                "reason": f"HFT execution error: {str(e)}"
            }
    
    async def _execute_standard_strategy(
        self, 
        signal: Dict[str, Any], 
        sltp_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute standard strategy with normal processing."""
        try:
            execution_result = {
                "strategy_type": signal.get("strategy_type"),
                "symbol": signal.get("symbol"),
                "action": signal.get("action"),
                "volume": signal.get("volume", 1.0),
                "sltp_data": sltp_result["sltp_data"],
                "priority": "MEDIUM",
                "execution_type": "standard",
                "execution_speed": "normal"
            }
            
            return {
                "success": True,
                "execution_type": "standard",
                "execution_result": execution_result
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error executing standard strategy: {e}")
            return {
                "success": False,
                "reason": f"Standard execution error: {str(e)}"
            }
    
    async def _track_enhanced_performance(
        self, 
        signal: Dict[str, Any], 
        execution_result: Dict[str, Any], 
        strategy_config: Dict[str, Any],
        quality_result: Dict[str, Any]
    ):
        """Track enhanced strategy-specific performance metrics."""
        try:
            strategy_type = signal.get("strategy_type", "unknown")
            symbol = signal.get("symbol", "unknown")
            
            # Update strategy performance tracking
            if strategy_type not in self.strategy_performance:
                self.strategy_performance[strategy_type] = {
                    "total_signals": 0,
                    "accepted_signals": 0,
                    "rejected_signals": 0,
                    "total_pnl": 0.0,
                    "win_rate": 0.0,
                    "avg_risk_reward": 0.0,
                    "last_update": time.time()
                }
            
            # Update counts
            self.strategy_performance[strategy_type]["total_signals"] += 1
            self.strategy_performance[strategy_type]["accepted_signals"] += 1
            self.strategy_performance[strategy_type]["last_update"] = time.time()
            
            if self.logger:
                self.logger.debug(f"✅ Enhanced performance tracking updated for {strategy_type} on {symbol}")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error tracking enhanced performance: {e}")
    
    def _create_rejection_response(self, signal_id: str, reason: str) -> Dict[str, Any]:
        """Create a standardized rejection response."""
        self.total_signals_processed += 1
        self.signals_rejected += 1
        
        return {
            "success": False,
            "reason": reason,
            "signal_id": signal_id,
            "enhancements_applied": ["rejection_handling"]
        }
    
    # ============= PUBLIC INTERFACE =============
    
    async def get_enhancement_status(self) -> Dict[str, Any]:
        """Get comprehensive enhancement manager status."""
        return {
            "enhancement_status": {
                "is_active": True,
                "total_signals_processed": self.total_signals_processed,
                "signals_accepted": self.signals_accepted,
                "signals_rejected": self.signals_rejected,
                "acceptance_rate": self.signals_accepted / max(self.total_signals_processed, 1)
            },
            "strategy_performance": self.strategy_performance,
            "component_health": {
                "sltp_calculator": self.sltp_calculator is not None,
                "rate_limiter": self.rate_limiter is not None,
                "signal_quality_assessor": self.signal_quality_assessor is not None,
                "session_manager": self.session_manager is not None,
                "ml_composer": self.ml_composer is not None,
                "online_generator": self.online_generator is not None,
                "strategy_learning_manager": self.strategy_learning_manager is not None,
                "strategy_adaptation_engine": self.strategy_adaptation_engine is not None
            },
            "last_update": time.time()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get module status for health checking."""
        return {
            "module": "Strategy Enhancement Manager",
            "is_active": True,
            "total_signals_processed": self.total_signals_processed,
            "signals_accepted": self.signals_accepted,
            "signals_rejected": self.signals_rejected,
            "components": {
                "sltp_calculator": self.sltp_calculator is not None,
                "rate_limiter": self.rate_limiter is not None,
                "signal_quality_assessor": self.signal_quality_assessor is not None,
                "session_manager": self.session_manager is not None,
                "ml_composer": self.ml_composer is not None,
                "online_generator": self.online_generator is not None,
                "strategy_learning_manager": self.strategy_learning_manager is not None,
                "strategy_adaptation_engine": self.strategy_adaptation_engine is not None
            },
            "strategy_performance": len(self.strategy_performance),
            "last_update": time.time()
        }
    
    # ============= LEARNING & COMPOSING METHODS =============
    
    async def compose_new_strategy(self, composition_request: Dict[str, Any]) -> Dict[str, Any]:
        """Compose a new trading strategy using ML composition."""
        try:
            if self.logger:
                self.logger.info(f"🔄 Composing new strategy: {composition_request.get('composition_type', 'unknown')}")
            
            # Use ML Composer to create new strategy
            composition_result = await self.ml_composer.compose_strategy(composition_request)
            
            if composition_result["success"]:
                # Learn from the composition
                await self.strategy_learning_manager.learn_from_strategy_execution(
                    composition_result["composed_strategy"], 
                    {"type": "composition", "result": composition_result}
                )
                
                if self.logger:
                    self.logger.info(f"✅ New strategy composed successfully: {composition_result['result_id']}")
            
            return composition_result
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error composing new strategy: {e}")
            return {
                "success": False,
                "reason": f"Strategy composition error: {str(e)}"
            }
    
    async def generate_online_strategy(self, generation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a new strategy online based on market conditions."""
        try:
            if self.logger:
                self.logger.info(f"🔄 Generating online strategy: {generation_request.get('generation_type', 'unknown')}")
            
            # Use Online Generator to create market-adaptive strategy
            generation_result = await self.online_generator.generate_strategy(generation_request)
            
            if generation_result["success"]:
                # Learn from the generation
                await self.strategy_learning_manager.learn_from_strategy_execution(
                    generation_result["generated_strategy"], 
                    {"type": "generation", "result": generation_result}
                )
                
                if self.logger:
                    self.logger.info(f"✅ Online strategy generated successfully: {generation_result['result_id']}")
            
            return generation_result
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error generating online strategy: {e}")
            return {
                "success": False,
                "reason": f"Online generation error: {str(e)}"
            }
    
    async def adapt_existing_strategy(self, adaptation_request: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt an existing strategy based on performance and market conditions."""
        try:
            if self.logger:
                self.logger.info(f"🔄 Adapting strategy: {adaptation_request.get('strategy_id', 'unknown')}")
            
            # Use Strategy Adaptation Engine to modify strategy
            adaptation_result = await self.strategy_adaptation_engine.adapt_strategy(adaptation_request)
            
            if adaptation_result["success"]:
                # Learn from the adaptation
                await self.strategy_learning_manager.learn_from_strategy_execution(
                    adaptation_result["adapted_strategy"], 
                    {"type": "adaptation", "result": adaptation_result}
                )
                
                if self.logger:
                    self.logger.info(f"✅ Strategy adapted successfully: {adaptation_result['result_id']}")
            
            return adaptation_result
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error adapting strategy: {e}")
            return {
                "success": False,
                "reason": f"Strategy adaptation error: {str(e)}"
            }
    
    async def learn_from_execution(self, strategy_data: Dict[str, Any], execution_result: Dict[str, Any]) -> bool:
        """Learn from strategy execution results."""
        try:
            # Use Strategy Learning Manager to learn from execution
            learning_result = await self.strategy_learning_manager.learn_from_strategy_execution(
                strategy_data, execution_result
            )
            
            if self.logger:
                self.logger.info(f"✅ Learning from execution completed: {learning_result}")
            
            return learning_result
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"❌ Error learning from execution: {e}")
            return False
