from typing import Dict, Any, Optional
from ...logs.strategy_engine_logger import StrategyEngineLogger
from .signal_processor import TradingSignalProcessor
from .flow_manager import FlowManager
import time

class TradingLogicExecutor:
    """Trading logic executor - consolidated from Core Agent."""
    
    def __init__(self, signal_processor: TradingSignalProcessor, flow_manager: FlowManager):
        self.signal_processor = signal_processor
        self.flow_manager = flow_manager
        self.logger = StrategyEngineLogger("trading_logic_executor")

    def initialize(self):
        """Initialize the trading logic executor."""
        self.logger.log_action("initialize", {"status": "starting"})
        try:
            # Initialize signal processor and flow manager
            if hasattr(self.signal_processor, 'initialize'):
                self.signal_processor.initialize()
            if hasattr(self.flow_manager, 'initialize'):
                self.flow_manager.initialize()
            self.logger.log_action("initialize", {"status": "completed"})
        except Exception as e:
            self.logger.log_action("initialize", {"status": "failed", "error": str(e)})
            raise

    def cleanup(self):
        """Cleanup the trading logic executor."""
        self.logger.log_action("cleanup", {"status": "starting"})
        try:
            # Cleanup signal processor and flow manager
            if hasattr(self.signal_processor, 'cleanup'):
                self.signal_processor.cleanup()
            if hasattr(self.flow_manager, 'cleanup'):
                self.flow_manager.cleanup()
            self.logger.log_action("cleanup", {"status": "completed"})
        except Exception as e:
            self.logger.log_action("cleanup", {"status": "failed", "error": str(e)})
            raise

    async def execute_trading_logic_tree(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute the logic tree for a trading signal."""
        self.logger.log_action("execute_trading_logic_tree", {"signal": signal})

        # Step 1: Validate trading signal
        if not self.signal_processor.validate_trading_signal(signal):
            self.logger.log_action("trading_signal_rejected", {"reason": "Invalid signal format"})
            return None

        # Step 2: Check risk compliance
        risk_check = await self.flow_manager._check_risk_compliance(signal)
        if not risk_check["passed"]:
            self.logger.log_action("trading_signal_rejected", {"reason": f"Risk violation: {risk_check['reason']}"})
            return None

        # Step 3: Process trading signal
        processed_signal = self.signal_processor.process_trading_signal(signal)
        if not processed_signal.get("valid", False):
            self.logger.log_action("trading_signal_rejected", {"reason": "Signal processing failed"})
            return None

        # Step 4: Execute trading flow
        result = await self.flow_manager.process_trading_signal(signal)
        if result and result.get("success"):
            self.logger.log_action("trading_logic_completed", {"result": result})
            return result
        else:
            self.logger.log_action("trading_logic_failed", {"result": result})
            return None

    async def execute_strategy_signal(self, strategy_signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a strategy-generated trading signal."""
        try:
            self.logger.log_action("execute_strategy_signal", {"strategy_signal": strategy_signal})
            
            # Validate strategy signal
            if not self._validate_strategy_signal(strategy_signal):
                self.logger.log_action("strategy_signal_rejected", {"reason": "Invalid strategy signal"})
                return None
            
            # Convert strategy signal to trading signal
            trading_signal = self._convert_strategy_to_trading_signal(strategy_signal)
            
            # Execute trading logic
            result = await self.execute_trading_logic_tree(trading_signal)
            
            if result:
                self.logger.log_action("strategy_signal_executed", {"result": result})
                return result
            else:
                self.logger.log_action("strategy_signal_execution_failed", {"strategy_signal": strategy_signal})
                return None
                
        except Exception as e:
            self.logger.log_action("strategy_signal_execution_error", {"error": str(e)})
            return None

    async def execute_arbitrage_signal(self, arbitrage_signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute an arbitrage trading signal."""
        try:
            self.logger.log_action("execute_arbitrage_signal", {"arbitrage_signal": arbitrage_signal})
            
            # Validate arbitrage signal
            if not self._validate_arbitrage_signal(arbitrage_signal):
                self.logger.log_action("arbitrage_signal_rejected", {"reason": "Invalid arbitrage signal"})
                return None
            
            # Convert arbitrage signal to trading signal
            trading_signal = self._convert_arbitrage_to_trading_signal(arbitrage_signal)
            
            # Execute trading logic
            result = await self.execute_trading_logic_tree(trading_signal)
            
            if result:
                self.logger.log_action("arbitrage_signal_executed", {"result": result})
                return result
            else:
                self.logger.log_action("arbitrage_signal_execution_failed", {"arbitrage_signal": arbitrage_signal})
                return None
                
        except Exception as e:
            self.logger.log_action("arbitrage_signal_execution_error", {"error": str(e)})
            return None

    async def execute_market_making_signal(self, mm_signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a market making trading signal."""
        try:
            self.logger.log_action("execute_market_making_signal", {"mm_signal": mm_signal})
            
            # Validate market making signal
            if not self._validate_market_making_signal(mm_signal):
                self.logger.log_action("mm_signal_rejected", {"reason": "Invalid market making signal"})
                return None
            
            # Convert market making signal to trading signal
            trading_signal = self._convert_mm_to_trading_signal(mm_signal)
            
            # Execute trading logic
            result = await self.execute_trading_logic_tree(trading_signal)
            
            if result:
                self.logger.log_action("mm_signal_executed", {"result": result})
                return result
            else:
                self.logger.log_action("mm_signal_execution_failed", {"mm_signal": mm_signal})
                return None
                
        except Exception as e:
            self.logger.log_action("mm_signal_execution_error", {"error": str(e)})
            return None

    # ============= VALIDATION METHODS =============
    
    def _validate_strategy_signal(self, strategy_signal: Dict[str, Any]) -> bool:
        """Validate strategy-generated signal."""
        try:
            required_fields = ["strategy_id", "signal_type", "parameters", "confidence"]
            return all(field in strategy_signal for field in required_fields)
        except Exception:
            return False
    
    def _validate_arbitrage_signal(self, arbitrage_signal: Dict[str, Any]) -> bool:
        """Validate arbitrage signal."""
        try:
            required_fields = ["arbitrage_type", "opportunity_id", "legs", "expected_profit"]
            return all(field in arbitrage_signal for field in required_fields)
        except Exception:
            return False
    
    def _validate_market_making_signal(self, mm_signal: Dict[str, Any]) -> bool:
        """Validate market making signal."""
        try:
            required_fields = ["quote_type", "symbol", "bid_price", "ask_price", "spread"]
            return all(field in mm_signal for field in required_fields)
        except Exception:
            return False

    # ============= CONVERSION METHODS =============
    
    def _convert_strategy_to_trading_signal(self, strategy_signal: Dict[str, Any]) -> Dict[str, Any]:
        """Convert strategy signal to trading signal format."""
        try:
            return {
                "signal_id": f"strategy_{strategy_signal.get('strategy_id')}_{int(time.time())}",
                "strategy": strategy_signal.get("signal_type", "unknown"),
                "params": strategy_signal.get("parameters", {}),
                "timestamp": time.time(),
                "source": "strategy_engine",
                "confidence": strategy_signal.get("confidence", 0.5)
            }
        except Exception as e:
            self.logger.log_action("strategy_conversion_error", {"error": str(e)})
            return {}
    
    def _convert_arbitrage_to_trading_signal(self, arbitrage_signal: Dict[str, Any]) -> Dict[str, Any]:
        """Convert arbitrage signal to trading signal format."""
        try:
            return {
                "signal_id": f"arbitrage_{arbitrage_signal.get('opportunity_id')}_{int(time.time())}",
                "strategy": "arbitrage",
                "params": {
                    "arbitrage_type": arbitrage_signal.get("arbitrage_type"),
                    "legs": arbitrage_signal.get("legs", []),
                    "expected_profit": arbitrage_signal.get("expected_profit", 0.0)
                },
                "timestamp": time.time(),
                "source": "arbitrage_detector"
            }
        except Exception as e:
            self.logger.log_action("arbitrage_conversion_error", {"error": str(e)})
            return {}
    
    def _convert_mm_to_trading_signal(self, mm_signal: Dict[str, Any]) -> Dict[str, Any]:
        """Convert market making signal to trading signal format."""
        try:
            return {
                "signal_id": f"mm_{mm_signal.get('symbol')}_{int(time.time())}",
                "strategy": "market_making",
                "params": {
                    "symbol": mm_signal.get("symbol"),
                    "bid_price": mm_signal.get("bid_price"),
                    "ask_price": mm_signal.get("ask_price"),
                    "spread": mm_signal.get("spread")
                },
                "timestamp": time.time(),
                "source": "market_maker"
            }
        except Exception as e:
            self.logger.log_action("mm_conversion_error", {"error": str(e)})
            return {}

    # ============= PUBLIC INTERFACE METHODS =============
    
    def get_trading_logic_status(self) -> Dict[str, Any]:
        """Get trading logic execution status."""
        try:
            return {
                "signal_processor_status": "active",
                "flow_manager_status": "active",
                "trading_logic_status": "active",
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.log_action("get_trading_logic_status_error", {"error": str(e)})
            return {"error": str(e)}
    
    async def get_execution_summary(self) -> Dict[str, Any]:
        """Get trading logic execution summary."""
        try:
            return {
                "signal_processor_stats": self.signal_processor.get_processing_stats(),
                "flow_manager_stats": self.flow_manager.get_flow_stats(),
                "trading_logic_status": "active",
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.log_action("get_execution_summary_error", {"error": str(e)})
            return {"error": str(e)}
