#!/usr/bin/env python3
"""
Performance Tracker
Tracks strategy performance metrics (PnL, Sharpe, drawdowns).
"""

import asyncio
import time
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from engine_agents.shared_utils import get_shared_logger, get_shared_redis

# Import consolidated trading functionality
from ..memory.trading_context import TradingContext
from ..learning.trading_research_engine import TradingResearchEngine

class PerformanceTracker:
    """Tracks and analyzes strategy performance metrics."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "performance_tracker")
        self.redis_conn = get_shared_redis()

        # Initialize consolidated trading components
        self.trading_context = TradingContext(config)
        self.trading_research_engine = TradingResearchEngine(config)

        # Performance tracking configuration
        self.tracking_interval = config.get("tracking_interval", 30)  # 30 seconds
        self.max_history = config.get("max_history", 1000)
        self.alert_thresholds = config.get("alert_thresholds", {
            "max_drawdown": -0.1,  # 10% max drawdown
            "min_sharpe": 0.5,     # Minimum Sharpe ratio
            "max_loss_rate": 0.4    # Maximum 40% loss rate
        })

        # Performance data storage
        self.performance_history: List[Dict[str, Any]] = []
        self.strategy_metrics: Dict[str, Dict[str, Any]] = {}
        self.alerts: List[Dict[str, Any]] = []

        # Tracking statistics
        self.stats = {
            "performance_checks": 0,
            "alerts_generated": 0,
            "strategies_tracked": 0,
            "tracking_errors": 0,
            "start_time": time.time()
        }

    async def initialize(self) -> bool:
        """Initialize the performance tracker."""
        try:
            self.logger.info("Initializing Performance Tracker...")
            
            # Initialize trading components
            await self.trading_context.initialize()
            await self.trading_research_engine.initialize()
            
            self.logger.info("Performance Tracker initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize performance tracker: {e}")
            return False

    async def track_performance(self, strategy_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Track strategy performance metrics (PnL, Sharpe, drawdowns)."""
        try:
            tracked_results = []
            
            for data in strategy_data:
                strategy_id = data.get("strategy_id", "unknown")
                symbol = data.get("symbol", "unknown")
                strategy_type = data.get("type", "unknown")
                
                # Get historical performance data from trading context
                historical_data = await self._get_strategy_history(strategy_id)
                
                # Calculate performance metrics
                performance_metrics = await self._calculate_performance_metrics(
                    strategy_id, symbol, strategy_type, historical_data
                )
                
                # Store performance data in trading context
                await self.trading_context.store_pnl_snapshot({
                    "strategy_id": strategy_id,
                    "symbol": symbol,
                    "strategy_type": strategy_type,
                    "performance_metrics": performance_metrics,
                    "timestamp": int(time.time())
                })
                
                # Check for performance alerts
                if await self._check_performance_alerts(performance_metrics):
                    alert = await self._flag_strategy(strategy_id, symbol, performance_metrics)
                    if alert:
                        self.alerts.append(alert)
                        self.stats["alerts_generated"] += 1
                
                # Update strategy metrics
                self.strategy_metrics[strategy_id] = performance_metrics
                
                tracked_results.append({
                    "strategy_id": strategy_id,
                    "symbol": symbol,
                    "strategy_type": strategy_type,
                    "performance_metrics": performance_metrics,
                    "timestamp": int(time.time())
                })
                
                self.stats["performance_checks"] += 1
            
            # Store performance history
            self.performance_history.extend(tracked_results)
            
            # Limit history size
            if len(self.performance_history) > self.max_history:
                self.performance_history = self.performance_history[-self.max_history:]
            
            self.logger.info(f"Tracked performance for {len(tracked_results)} strategies")
            return tracked_results
            
        except Exception as e:
            self.logger.error(f"Error tracking performance: {e}")
            self.stats["tracking_errors"] += 1
            return []

    async def _get_strategy_history(self, strategy_id: str) -> List[Dict[str, Any]]:
        """Get historical performance data for a strategy."""
        try:
            # Get recent signals and execution results from trading context
            signals = await self.trading_context.get_recent_signals(strategy_id, limit=100)
            execution_results = await self.trading_context.get_recent_execution_results(strategy_id, limit=100)
            pnl_snapshots = await self.trading_context.get_recent_pnl_snapshots(strategy_id, limit=100)
            
            return signals + execution_results + pnl_snapshots
            
        except Exception as e:
            self.logger.error(f"Error getting strategy history for {strategy_id}: {e}")
            return []

    async def _calculate_performance_metrics(self, strategy_id: str, symbol: str, 
                                           strategy_type: str, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics."""
        try:
            if not historical_data:
                return {
                    "strategy_id": strategy_id,
                    "symbol": symbol,
                    "strategy_type": strategy_type,
                    "total_pnl": 0.0,
                    "sharpe_ratio": 0.0,
                    "max_drawdown": 0.0,
                    "win_rate": 0.0,
                    "profit_factor": 0.0,
                    "total_trades": 0,
                    "successful_trades": 0,
                    "average_trade": 0.0,
                    "volatility": 0.0,
                    "calmar_ratio": 0.0
                }
            
            # Extract PnL data
            pnl_data = []
            trade_results = []
            
            for data in historical_data:
                if "pnl" in data:
                    pnl_data.append(data["pnl"])
                if "success" in data:
                    trade_results.append(data["success"])
                if "execution_data" in data and "pnl" in data["execution_data"]:
                    pnl_data.append(data["execution_data"]["pnl"])
                if "performance_data" in data and "total_pnl" in data["performance_data"]:
                    pnl_data.append(data["performance_data"]["total_pnl"])
            
            if not pnl_data:
                return {
                    "strategy_id": strategy_id,
                    "symbol": symbol,
                    "strategy_type": strategy_type,
                    "total_pnl": 0.0,
                    "sharpe_ratio": 0.0,
                    "max_drawdown": 0.0,
                    "win_rate": 0.0,
                    "profit_factor": 0.0,
                    "total_trades": 0,
                    "successful_trades": 0,
                    "average_trade": 0.0,
                    "volatility": 0.0,
                    "calmar_ratio": 0.0
                }
            
            # Calculate basic metrics
            total_pnl = sum(pnl_data)
            total_trades = len(pnl_data)
            successful_trades = len([p for p in pnl_data if p > 0])
            win_rate = successful_trades / total_trades if total_trades > 0 else 0.0
            average_trade = total_pnl / total_trades if total_trades > 0 else 0.0
            
            # Calculate Sharpe ratio
            if len(pnl_data) > 1:
                returns = np.diff(pnl_data)
                if len(returns) > 0:
                    sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0.0
                    volatility = np.std(returns)
                else:
                    sharpe_ratio = 0.0
                    volatility = 0.0
            else:
                sharpe_ratio = 0.0
                volatility = 0.0
            
            # Calculate max drawdown
            cumulative_pnl = np.cumsum(pnl_data)
            running_max = np.maximum.accumulate(cumulative_pnl)
            drawdowns = cumulative_pnl - running_max
            max_drawdown = np.min(drawdowns) if len(drawdowns) > 0 else 0.0
            
            # Calculate profit factor
            gross_profit = sum([p for p in pnl_data if p > 0])
            gross_loss = abs(sum([p for p in pnl_data if p < 0]))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
            
            # Calculate Calmar ratio
            calmar_ratio = total_pnl / abs(max_drawdown) if max_drawdown != 0 else 0.0
            
            return {
                "strategy_id": strategy_id,
                "symbol": symbol,
                "strategy_type": strategy_type,
                "total_pnl": float(total_pnl),
                "sharpe_ratio": float(sharpe_ratio),
                "max_drawdown": float(max_drawdown),
                "win_rate": float(win_rate),
                "profit_factor": float(profit_factor),
                "total_trades": total_trades,
                "successful_trades": successful_trades,
                "average_trade": float(average_trade),
                "volatility": float(volatility),
                "calmar_ratio": float(calmar_ratio),
                "last_calculation": int(time.time())
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics for {strategy_id}: {e}")
            return {
                "strategy_id": strategy_id,
                "symbol": symbol,
                "strategy_type": strategy_type,
                "error": str(e)
            }

    async def _check_performance_alerts(self, performance_metrics: Dict[str, Any]) -> bool:
        """Check if performance metrics trigger alerts."""
        try:
            max_drawdown = performance_metrics.get("max_drawdown", 0.0)
            sharpe_ratio = performance_metrics.get("sharpe_ratio", 0.0)
            win_rate = performance_metrics.get("win_rate", 0.0)
            
            # Check drawdown threshold
            if max_drawdown < self.alert_thresholds["max_drawdown"]:
                return True
            
            # Check Sharpe ratio threshold
            if sharpe_ratio < self.alert_thresholds["min_sharpe"]:
                return True
            
            # Check loss rate threshold
            if (1 - win_rate) > self.alert_thresholds["max_loss_rate"]:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking performance alerts: {e}")
            return False

    async def _flag_strategy(self, strategy_id: str, symbol: str, 
                           performance_metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Flag a strategy for poor performance."""
        try:
            alert = {
                "type": "performance_alert",
                "strategy_id": strategy_id,
                "symbol": symbol,
                "alert_timestamp": int(time.time()),
                "performance_metrics": performance_metrics,
                "alert_reasons": []
            }
            
            # Determine alert reasons
            if performance_metrics.get("max_drawdown", 0.0) < self.alert_thresholds["max_drawdown"]:
                alert["alert_reasons"].append("excessive_drawdown")
            
            if performance_metrics.get("sharpe_ratio", 0.0) < self.alert_thresholds["min_sharpe"]:
                alert["alert_reasons"].append("low_sharpe_ratio")
            
            if (1 - performance_metrics.get("win_rate", 0.0)) > self.alert_thresholds["max_loss_rate"]:
                alert["alert_reasons"].append("high_loss_rate")
            
            # Store alert in trading context
            await self.trading_context.store_signal({
                "type": "performance_alert",
                "alert_data": alert,
                "timestamp": int(time.time())
            })
            
            self.logger.warning(f"Performance alert generated for strategy {strategy_id}: {alert['alert_reasons']}")
            return alert
            
        except Exception as e:
            self.logger.error(f"Error flagging strategy {strategy_id}: {e}")
            return None

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        try:
            # Use trading research engine to analyze performance patterns
            performance_analysis = await self.trading_research_engine.analyze_trading_performance(
                self.performance_history
            )
            
            return {
                "stats": self.stats,
                "performance_history_count": len(self.performance_history),
                "strategies_tracked_count": len(self.strategy_metrics),
                "alerts_count": len(self.alerts),
                "performance_analysis": performance_analysis,
                "alert_thresholds": self.alert_thresholds,
                "uptime": time.time() - self.stats["start_time"]
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {"error": str(e)}

    async def get_strategy_performance(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get performance metrics for a specific strategy."""
        return self.strategy_metrics.get(strategy_id)

    async def cleanup(self):
        """Clean up resources."""
        try:
            await self.trading_context.cleanup()
            await self.trading_research_engine.cleanup()
            self.logger.info("Performance Tracker cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")