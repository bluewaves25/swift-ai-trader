#!/usr/bin/env python3
"""
Strategy Applicator - Core Strategy Application Component
Applies trading strategies and integrates with consolidated trading functionality.
Focuses purely on strategy-specific tasks, delegating risk management to the risk management agent.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import deque

# Import consolidated trading functionality
from ..trading.logic_executor import TradingLogicExecutor
from ..trading.signal_processor import TradingSignalProcessor
from ..trading.flow_manager import TradingFlowManager
from ..trading.memory.trading_context import TradingContext
from ..trading.interfaces.agent_io import TradingAgentIO

@dataclass
class ApplicationRequest:
    """A strategy application request."""
    request_id: str
    strategy_id: str
    market_data: Dict[str, Any]
    application_type: str  # live, paper, backtest
    parameters: Dict[str, Any]
    status: str = "pending"
    created_at: float = None
    priority: int = 5
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

@dataclass
class ApplicationResult:
    """Result of strategy application."""
    result_id: str
    request_id: str
    strategy_id: str
    application_type: str
    signals_generated: List[Dict[str, Any]]
    trades_executed: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    application_duration: float
    timestamp: float
    success: bool

class StrategyApplicator:
    """Applies trading strategies to market data.
    
    Focuses purely on strategy-specific tasks:
    - Strategy application and execution
    - Signal generation and processing
    - Performance tracking
    - Strategy optimization
    
    Risk management is delegated to the risk management agent.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize consolidated trading components
        self.trading_signal_processor = TradingSignalProcessor(config)
        self.trading_flow_manager = TradingFlowManager(config)
        self.trading_logic_executor = TradingLogicExecutor(self.trading_signal_processor, self.trading_flow_manager)
        self.trading_context = TradingContext(max_history=1000)  # Fixed: pass integer instead of config
        self.trading_agent_io = TradingAgentIO(config)
        
        # Application state
        self.application_queue: deque = deque(maxlen=100)
        self.active_applications: Dict[str, ApplicationRequest] = {}
        self.application_results: Dict[str, List[ApplicationResult]] = {}
        self.application_history: deque = deque(maxlen=1000)
        
        # Application settings (strategy-specific only)
        self.application_settings = {
            "max_concurrent_applications": 10,
            "application_timeout": 300,  # 5 minutes
            "auto_application": True,
            "performance_threshold": 0.6,
            "strategy_parameters": {
                "max_position_size": 100000,  # Strategy-level position sizing
                "signal_confidence_threshold": 0.7,
                "strategy_timeout": 60
            }
        }
        
        # Application statistics
        self.application_stats = {
            "total_applications": 0,
            "successful_applications": 0,
            "failed_applications": 0,
            "total_signals": 0,
            "total_trades": 0,
            "average_performance": 0.0
        }
        
    async def initialize(self):
        """Initialize the strategy applicator."""
        try:
            # Initialize trading components (these are not async)
            self.trading_logic_executor.initialize()
            self.trading_context.initialize()
            self.trading_agent_io.initialize()
            
            # Load application settings
            await self._load_application_settings()
            
            # Initialize application tracking
            await self._initialize_application_tracking()
            
            print("✅ Strategy Applicator initialized")
            
        except Exception as e:
            print(f"❌ Error initializing Strategy Applicator: {e}")
            raise
    
    async def _initialize_trading_integration(self):
        """Initialize trading integration components."""
        # This is now handled in the main initialize method
        pass
    
    async def _load_application_settings(self):
        """Load application settings from configuration."""
        # Load strategy-specific settings only
        strategy_config = self.config.get("strategy_engine", {}).get("applicator", {})
        self.application_settings.update(strategy_config)
    
    async def _initialize_application_tracking(self):
        """Initialize application tracking and monitoring."""
        # Initialize application tracking systems
        pass

    async def apply_strategy(self, strategy_id: str, market_data: Dict[str, Any], 
                           application_type: str = "paper", parameters: Dict[str, Any] = None) -> ApplicationResult:
        """Apply a trading strategy to market data.
        
        This method focuses purely on strategy application:
        - Generates trading signals based on strategy logic
        - Processes market data through strategy algorithms
        - Tracks strategy performance
        - Delegates risk validation to risk management agent
        """
        try:
            # Create application request
            request = ApplicationRequest(
                request_id=f"app_{strategy_id}_{int(time.time())}",
                strategy_id=strategy_id,
                market_data=market_data,
                application_type=application_type,
                parameters=parameters or {}
            )
            
            # Add to application queue
            self.application_queue.append(request)
            
            # Process application
            result = await self._process_strategy_application(request)
            
            # Update statistics
            self.application_stats["total_applications"] += 1
            if result.success:
                self.application_stats["successful_applications"] += 1
            else:
                self.application_stats["failed_applications"] += 1
            
            self.application_stats["total_signals"] += len(result.signals_generated)
            self.application_stats["total_trades"] += len(result.trades_executed)
            
            # Store result
            if strategy_id not in self.application_results:
                self.application_results[strategy_id] = []
            self.application_results[strategy_id].append(result)
            
            # Store in trading context
            self.trading_context.store_signal({
                "type": "strategy_application",
                "strategy_id": strategy_id,
                "application_result": result,
                "timestamp": int(time.time())
            })
            
            return result
            
        except Exception as e:
            print(f"❌ Error applying strategy {strategy_id}: {e}")
            # Return failed result
            return ApplicationResult(
                result_id=f"failed_{strategy_id}_{int(time.time())}",
                request_id=request.request_id if 'request' in locals() else "unknown",
                strategy_id=strategy_id,
                application_type=application_type,
                signals_generated=[],
                trades_executed=[],
                performance_metrics={},
                application_duration=0.0,
                timestamp=time.time(),
                success=False
            )

    async def _process_strategy_application(self, request: ApplicationRequest) -> ApplicationResult:
        """Process a strategy application request."""
        start_time = time.time()
        
        try:
            # Execute trading logic through consolidated trading system
            signals = await self.trading_logic_executor.execute_trading_logic_tree({
                "type": "strategy_application",
                "strategy_id": request.strategy_id,
                "market_data": request.market_data,
                "parameters": request.parameters
            })
            
            # Generate trading signals (strategy-specific logic)
            generated_signals = await self._generate_strategy_signals(
                request.strategy_id, 
                request.market_data, 
                signals
            )
            
            # Process signals through trading flow (delegates risk management)
            processed_signals = await self._process_signals_through_trading_flow(generated_signals)
            
            # Calculate performance metrics (strategy-specific only)
            performance_metrics = await self._calculate_strategy_performance(
                request.strategy_id, 
                processed_signals
            )
            
            # Create application result
            result = ApplicationResult(
                result_id=f"result_{request.request_id}",
                request_id=request.request_id,
                strategy_id=request.strategy_id,
                application_type=request.application_type,
                signals_generated=generated_signals,
                trades_executed=processed_signals,
                performance_metrics=performance_metrics,
                application_duration=time.time() - start_time,
                timestamp=time.time(),
                success=True
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Error processing strategy application: {e}")
            # Return failed result
            return ApplicationResult(
                result_id=f"failed_{request.request_id}",
                request_id=request.request_id,
                strategy_id=request.strategy_id,
                application_type=request.application_type,
                signals_generated=[],
                trades_executed=[],
                performance_metrics={},
                application_duration=time.time() - start_time,
                timestamp=time.time(),
                success=False
            )

    async def _generate_strategy_signals(self, strategy_id: str, market_data: Dict[str, Any], 
                                       logic_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate trading signals based on strategy logic.
        
        This is purely strategy-specific logic - no risk management here.
        """
        try:
            signals = []
            
            # Process logic results to generate signals
            for result in logic_results:
                if result.get("type") == "trading_signal":
                    signal = {
                        "signal_id": f"signal_{strategy_id}_{int(time.time())}",
                        "strategy_id": strategy_id,
                        "symbol": result.get("symbol", "unknown"),
                        "action": result.get("action", "hold"),
                        "entry_price": result.get("entry_price", 0.0),
                        "confidence": result.get("confidence", 0.0),
                        "strategy_parameters": result.get("parameters", {}),
                        "timestamp": int(time.time())
                    }
                    signals.append(signal)
            
            return signals
            
        except Exception as e:
            print(f"❌ Error generating strategy signals: {e}")
            return []

    async def _process_signals_through_trading_flow(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process signals through the trading flow.
        
        This delegates risk management to the risk management agent.
        """
        try:
            processed_signals = []
            
            for signal in signals:
                # Send signal to risk management agent for validation
                risk_validation = await self.trading_agent_io.send_to_risk({
                    "type": "signal_validation",
                    "signal": signal,
                    "timestamp": int(time.time())
                })
                
                if risk_validation.get("approved", False):
                    # Signal approved by risk management
                    processed_signal = signal.copy()
                    processed_signal["risk_approved"] = True
                    processed_signal["risk_score"] = risk_validation.get("risk_score", 0.0)
                    processed_signals.append(processed_signal)
                else:
                    # Signal rejected by risk management
                    rejected_signal = signal.copy()
                    rejected_signal["risk_approved"] = False
                    rejected_signal["rejection_reason"] = risk_validation.get("rejection_reason", "unknown")
                    processed_signals.append(rejected_signal)
            
            return processed_signals
            
        except Exception as e:
            print(f"❌ Error processing signals through trading flow: {e}")
            return signals  # Return original signals if processing fails

    async def _calculate_strategy_performance(self, strategy_id: str, 
                                           signals: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate strategy performance metrics.
        
        Focuses on strategy-specific metrics, not risk metrics.
        """
        try:
            if not signals:
                return {
                    "signal_count": 0,
                    "approval_rate": 0.0,
                    "average_confidence": 0.0,
                    "strategy_efficiency": 0.0
                }
            
            # Calculate strategy-specific metrics
            total_signals = len(signals)
            approved_signals = len([s for s in signals if s.get("risk_approved", False)])
            approval_rate = approved_signals / total_signals if total_signals > 0 else 0.0
            
            confidences = [s.get("confidence", 0.0) for s in signals]
            average_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Strategy efficiency (based on signal quality, not P&L)
            strategy_efficiency = approval_rate * average_confidence
            
            return {
                "signal_count": total_signals,
                "approval_rate": approval_rate,
                "average_confidence": average_confidence,
                "strategy_efficiency": strategy_efficiency
            }
            
        except Exception as e:
            print(f"❌ Error calculating strategy performance: {e}")
            return {}

    async def get_application_status(self, strategy_id: str = None) -> Dict[str, Any]:
        """Get application status and statistics."""
        if strategy_id:
            return {
                "strategy_id": strategy_id,
                "active_applications": len([a for a in self.active_applications.values() if a.strategy_id == strategy_id]),
                "application_results": len(self.application_results.get(strategy_id, [])),
                "performance_metrics": self.application_results.get(strategy_id, [{}])[-1].get("performance_metrics", {}) if self.application_results.get(strategy_id) else {}
            }
        else:
            return {
                "total_applications": self.application_stats["total_applications"],
                "successful_applications": self.application_stats["successful_applications"],
                "failed_applications": self.application_stats["failed_applications"],
                "total_signals": self.application_stats["total_signals"],
                "total_trades": self.application_stats["total_trades"],
                "average_performance": self.application_stats["average_performance"],
                "queue_size": len(self.application_queue),
                "active_applications": len(self.active_applications)
            }

    async def cleanup(self):
        """Clean up resources."""
        try:
            self.trading_logic_executor.cleanup()
            await self.trading_context.cleanup()
            self.trading_agent_io.cleanup()
            print("✅ Strategy Applicator cleaned up")
        except Exception as e:
            print(f"❌ Error cleaning up Strategy Applicator: {e}")
