from typing import Dict, Any, List, Optional
from collections import deque
from ...logs.strategy_engine_logger import StrategyEngineLogger
import time

class TradingContext:
    """Trading context - consolidated from Core Agent."""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.signals = deque(maxlen=max_history)
        self.rejections = deque(maxlen=max_history)
        self.pnl_snapshots = deque(maxlen=max_history)
        self.trade_commands = deque(maxlen=max_history)
        self.execution_results = deque(maxlen=max_history)
        self.logger = StrategyEngineLogger("trading_context")
        
    async def initialize(self):
        """Initialize the trading context."""
        try:
            # Initialize with empty state
            self.logger.log_action("initialize", {"max_history": self.max_history})
            return True
        except Exception as e:
            self.logger.log_action("initialize_error", {"error": str(e)})
            return False

    def store_signal(self, signal: Dict[str, Any]):
        """Store a trading signal."""
        self.signals.append(signal)
        self.logger.log_action("store_signal", {
            "signal_id": signal.get("signal_id"),
            "strategy": signal.get("strategy")
        })

    def store_rejection(self, signal_id: str, reason: str):
        """Store a rejected signal with reason."""
        rejection = {
            "signal_id": signal_id,
            "reason": reason,
            "timestamp": time.time()
        }
        self.rejections.append(rejection)
        self.logger.log_action("store_rejection", {
            "signal_id": signal_id, 
            "reason": reason
        })

    def store_pnl_snapshot(self, snapshot: Dict[str, Any]):
        """Store a PnL snapshot."""
        self.pnl_snapshots.append(snapshot)
        self.logger.log_action("store_pnl", {
            "snapshot": snapshot,
            "timestamp": time.time()
        })

    def store_trade_command(self, trade_command: Dict[str, Any]):
        """Store a trade command."""
        self.trade_commands.append(trade_command)
        self.logger.log_action("store_trade_command", {
            "command_id": trade_command.get("command_id"),
            "symbol": trade_command.get("symbol"),
            "action": trade_command.get("action")
        })

    def store_execution_result(self, execution_result: Dict[str, Any]):
        """Store an execution result."""
        self.execution_results.append(execution_result)
        self.logger.log_action("store_execution_result", {
            "command_id": execution_result.get("command_id"),
            "status": execution_result.get("status"),
            "timestamp": time.time()
        })

    def get_recent_signals(self) -> List[Dict[str, Any]]:
        """Get recent signals."""
        return list(self.signals)

    def get_recent_rejections(self) -> List[Dict[str, Any]]:
        """Get recent rejections."""
        return list(self.rejections)

    def get_recent_pnl(self) -> List[Dict[str, Any]]:
        """Get recent PnL snapshots."""
        return list(self.pnl_snapshots)

    def get_recent_trade_commands(self) -> List[Dict[str, Any]]:
        """Get recent trade commands."""
        return list(self.trade_commands)

    def get_recent_execution_results(self) -> List[Dict[str, Any]]:
        """Get recent execution results."""
        return list(self.execution_results)

    def get_signal_by_id(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """Get signal by ID."""
        for signal in self.signals:
            if signal.get("signal_id") == signal_id:
                return signal
        return None

    def get_trade_command_by_id(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Get trade command by ID."""
        for command in self.trade_commands:
            if command.get("command_id") == command_id:
                return command
        return None

    def get_execution_result_by_command_id(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Get execution result by command ID."""
        for result in self.execution_results:
            if result.get("command_id") == command_id:
                return result
        return None

    def get_signals_by_strategy(self, strategy: str) -> List[Dict[str, Any]]:
        """Get signals by strategy type."""
        return [
            signal for signal in self.signals 
            if signal.get("strategy") == strategy
        ]

    def get_trade_commands_by_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """Get trade commands by symbol."""
        return [
            command for command in self.trade_commands 
            if command.get("symbol") == symbol
        ]

    def get_rejection_reasons_summary(self) -> Dict[str, int]:
        """Get summary of rejection reasons."""
        rejection_counts = {}
        for rejection in self.rejections:
            reason = rejection.get("reason", "unknown")
            rejection_counts[reason] = rejection_counts.get(reason, 0) + 1
        return rejection_counts

    def get_strategy_performance_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get performance summary by strategy."""
        strategy_summary = {}
        
        for signal in self.signals:
            strategy = signal.get("strategy", "unknown")
            if strategy not in strategy_summary:
                strategy_summary[strategy] = {
                    "total_signals": 0,
                    "rejected_signals": 0,
                    "executed_signals": 0
                }
            
            strategy_summary[strategy]["total_signals"] += 1
            
            # Check if signal was rejected
            signal_id = signal.get("signal_id")
            if any(r.get("signal_id") == signal_id for r in self.rejections):
                strategy_summary[strategy]["rejected_signals"] += 1
            else:
                strategy_summary[strategy]["executed_signals"] += 1
        
        return strategy_summary

    def get_symbol_trading_summary(self) -> Dict[str, Dict[str, Any]]:
        """Get trading summary by symbol."""
        symbol_summary = {}
        
        for command in self.trade_commands:
            symbol = command.get("symbol", "unknown")
            if symbol not in symbol_summary:
                symbol_summary[symbol] = {
                    "total_commands": 0,
                    "buy_commands": 0,
                    "sell_commands": 0,
                    "close_commands": 0,
                    "total_volume": 0.0
                }
            
            symbol_summary[symbol]["total_commands"] += 1
            action = command.get("action", "unknown")
            
            if action == "buy":
                symbol_summary[symbol]["buy_commands"] += 1
            elif action == "sell":
                symbol_summary[symbol]["sell_commands"] += 1
            elif action == "close":
                symbol_summary[symbol]["close_commands"] += 1
            
            # Add volume
            amount = command.get("amount", 0.0)
            symbol_summary[symbol]["total_volume"] += amount
        
        return symbol_summary
        
    async def cleanup(self):
        """Clean up the trading context."""
        try:
            # Clear all data
            self.signals.clear()
            self.rejections.clear()
            self.pnl_snapshots.clear()
            self.trade_commands.clear()
            self.execution_results.clear()
            self.logger.log_action("cleanup", {"status": "completed"})
            return True
        except Exception as e:
            self.logger.log_action("cleanup_error", {"error": str(e)})
            return False

    def get_execution_performance_summary(self) -> Dict[str, Any]:
        """Get execution performance summary."""
        total_commands = len(self.trade_commands)
        total_results = len(self.execution_results)
        
        if total_commands == 0:
            return {"error": "No trade commands found"}
        
        successful_executions = 0
        failed_executions = 0
        
        for result in self.execution_results:
            status = result.get("status", "unknown")
            if status in ["success", "executed", "filled"]:
                successful_executions += 1
            else:
                failed_executions += 1
        
        execution_rate = successful_executions / total_commands if total_commands > 0 else 0.0
        
        return {
            "total_commands": total_commands,
            "total_execution_results": total_results,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "execution_rate": execution_rate,
            "missing_results": total_commands - total_results
        }

    def get_context_summary(self) -> Dict[str, Any]:
        """Get comprehensive trading context summary."""
        try:
            return {
                "total_signals": len(self.signals),
                "total_rejections": len(self.rejections),
                "total_pnl_snapshots": len(self.pnl_snapshots),
                "total_trade_commands": len(self.trade_commands),
                "total_execution_results": len(self.execution_results),
                "context_size": self.max_history,
                "rejection_reasons": self.get_rejection_reasons_summary(),
                "strategy_performance": self.get_strategy_performance_summary(),
                "symbol_trading": self.get_symbol_trading_summary(),
                "execution_performance": self.get_execution_performance_summary(),
                "timestamp": time.time()
            }
        except Exception as e:
            self.logger.log_action("get_context_summary_error", {"error": str(e)})
            return {"error": str(e)}

    def clear_context(self):
        """Clear all stored trading context."""
        self.signals.clear()
        self.rejections.clear()
        self.pnl_snapshots.clear()
        self.trade_commands.clear()
        self.execution_results.clear()
        self.logger.log_action("clear_trading_context", {})

    def export_context(self) -> Dict[str, Any]:
        """Export trading context for external use."""
        try:
            return {
                "signals": list(self.signals),
                "rejections": list(self.rejections),
                "pnl_snapshots": list(self.pnl_snapshots),
                "trade_commands": list(self.trade_commands),
                "execution_results": list(self.execution_results),
                "export_timestamp": time.time()
            }
        except Exception as e:
            self.logger.log_action("export_context_error", {"error": str(e)})
            return {"error": str(e)}

    def import_context(self, context_data: Dict[str, Any]):
        """Import trading context from external source."""
        try:
            if "signals" in context_data:
                self.signals.extend(context_data["signals"])
            if "rejections" in context_data:
                self.rejections.extend(context_data["rejections"])
            if "pnl_snapshots" in context_data:
                self.pnl_snapshots.extend(context_data["pnl_snapshots"])
            if "trade_commands" in context_data:
                self.trade_commands.extend(context_data["trade_commands"])
            if "execution_results" in context_data:
                self.execution_results.extend(context_data["execution_results"])
            
            self.logger.log_action("import_context", {
                "imported_items": len(context_data),
                "timestamp": time.time()
            })
            
        except Exception as e:
            self.logger.log_action("import_context_error", {"error": str(e)})
