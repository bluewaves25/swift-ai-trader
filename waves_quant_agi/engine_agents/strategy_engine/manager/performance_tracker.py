#!/usr/bin/env python3
"""
Performance Tracker - Fixed and Enhanced
Tracks strategy performance metrics and flags underperforming strategies.
"""

from typing import Dict, Any, List, Optional
import time
import numpy as np
from engine_agents.shared_utils import get_shared_redis, get_shared_logger

class PerformanceTracker:
    """Performance tracker for monitoring strategy performance."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "performance_tracker")
        self.redis_conn = get_shared_redis()
        
        # Performance thresholds
        self.sharpe_threshold = config.get("sharpe_threshold", 1.0)
        self.drawdown_threshold = config.get("drawdown_threshold", 0.1)
        self.return_threshold = config.get("return_threshold", 0.05)
        self.volatility_threshold = config.get("volatility_threshold", 0.3)
        
        # Performance tracking state
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}
        self.alert_history: List[Dict[str, Any]] = []
        
        self.stats = {
            "strategies_tracked": 0,
            "performance_alerts": 0,
            "metrics_calculated": 0,
            "errors": 0,
            "start_time": time.time()
        }

    async def track_performance(self, strategy_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Track strategy performance metrics (PnL, Sharpe, drawdowns)."""
        try:
            performances = []
            
            for data in strategy_data:
                strategy_id = data.get("strategy_id", "unknown")
                symbol = data.get("symbol", "unknown")
                strategy_type = data.get("type", "unknown")
                
                # Get historical performance data
                historical_data = await self._get_strategy_history(strategy_id)
                
                # Calculate performance metrics
                performance_metrics = await self._calculate_performance_metrics(
                    strategy_id, symbol, strategy_type, historical_data
                )
                
                if performance_metrics:
                    performances.append(performance_metrics)
                    
                    # Store performance metrics
                    await self._store_performance_metrics(strategy_id, performance_metrics)
                    
                    # Check for performance alerts
                    if await self._check_performance_alerts(performance_metrics):
                        await self._flag_strategy(strategy_id, symbol, performance_metrics)
                    
                    self.stats["strategies_tracked"] += 1
                    self.stats["metrics_calculated"] += 1

            self.logger.info(f"Tracked performance for {len(performances)} strategies")
            return performances
            
        except Exception as e:
            self.logger.error(f"Error tracking performance: {e}")
            self.stats["errors"] += 1
            return []

    async def _get_strategy_history(self, strategy_id: str) -> List[Dict[str, Any]]:
        """Get historical performance data for a strategy."""
        try:
            # Get from Redis
            history_key = f"strategy_engine:performance_history:{strategy_id}"
            history_data = self.redis_conn.get(history_key)
            
            if history_data:
                import json
                return json.loads(history_data)
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting strategy history: {e}")
            return []

    async def _calculate_performance_metrics(self, strategy_id: str, symbol: str, 
                                           strategy_type: str, historical_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Calculate comprehensive performance metrics."""
        try:
            if not historical_data:
                return None
            
            # Extract returns and other metrics
            returns = [data.get("return", 0.0) for data in historical_data]
            pnl_values = [data.get("pnl", 0.0) for data in historical_data]
            volumes = [data.get("volume", 0.0) for data in historical_data]
            
            if not returns or all(r == 0.0 for r in returns):
                return None
            
            # Calculate basic metrics
            sharpe_ratio = self._calculate_sharpe(returns)
            max_drawdown = self._calculate_max_drawdown(returns)
            total_return = sum(returns)
            avg_return = np.mean(returns)
            volatility = np.std(returns) if len(returns) > 1 else 0.0
            
            # Calculate advanced metrics
            win_rate = self._calculate_win_rate(returns)
            profit_factor = self._calculate_profit_factor(returns)
            max_consecutive_losses = self._calculate_max_consecutive_losses(returns)
            
            # Calculate position sizing metrics
            avg_position_size = np.mean(volumes) if volumes else 0.0
            position_efficiency = self._calculate_position_efficiency(pnl_values, volumes)
            
            performance = {
                "type": "performance_metrics",
                "strategy_id": strategy_id,
                "symbol": symbol,
                "strategy_type": strategy_type,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown,
                "total_return": total_return,
                "avg_return": avg_return,
                "volatility": volatility,
                "win_rate": win_rate,
                "profit_factor": profit_factor,
                "max_consecutive_losses": max_consecutive_losses,
                "avg_position_size": avg_position_size,
                "position_efficiency": position_efficiency,
                "timestamp": int(time.time()),
                "description": f"Performance for {strategy_id} ({symbol}): Sharpe {sharpe_ratio:.2f}, Return {total_return:.4f}"
            }
            
            return performance
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            return None

    def _calculate_sharpe(self, returns: List[float]) -> float:
        """Calculate Sharpe ratio for strategy returns."""
        try:
            if not returns or len(returns) < 2:
                return 0.0
            
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            
            if std_return == 0:
                return 0.0
            
            # Annualized Sharpe ratio (assuming daily returns)
            return (mean_return / std_return) * np.sqrt(252)
            
        except Exception as e:
            self.logger.error(f"Error calculating Sharpe ratio: {e}")
            return 0.0

    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown from returns."""
        try:
            if not returns:
                return 0.0
            
            cumulative = np.cumsum(returns)
            peak = np.maximum.accumulate(cumulative)
            drawdown = (peak - cumulative) / peak
            
            return float(np.max(drawdown)) if len(drawdown) > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating max drawdown: {e}")
            return 0.0

    def _calculate_win_rate(self, returns: List[float]) -> float:
        """Calculate win rate (percentage of positive returns)."""
        try:
            if not returns:
                return 0.0
            
            positive_returns = sum(1 for r in returns if r > 0)
            return positive_returns / len(returns)
            
        except Exception as e:
            self.logger.error(f"Error calculating win rate: {e}")
            return 0.0

    def _calculate_profit_factor(self, returns: List[float]) -> float:
        """Calculate profit factor (gross profit / gross loss)."""
        try:
            if not returns:
                return 0.0
            
            gross_profit = sum(r for r in returns if r > 0)
            gross_loss = abs(sum(r for r in returns if r < 0))
            
            return gross_profit / gross_loss if gross_loss > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating profit factor: {e}")
            return 0.0

    def _calculate_max_consecutive_losses(self, returns: List[float]) -> int:
        """Calculate maximum consecutive losses."""
        try:
            if not returns:
                return 0
            
            max_consecutive = 0
            current_consecutive = 0
            
            for return_val in returns:
                if return_val < 0:
                    current_consecutive += 1
                    max_consecutive = max(max_consecutive, current_consecutive)
                else:
                    current_consecutive = 0
            
            return max_consecutive
            
        except Exception as e:
            self.logger.error(f"Error calculating max consecutive losses: {e}")
            return 0

    def _calculate_position_efficiency(self, pnl_values: List[float], volumes: List[float]) -> float:
        """Calculate position efficiency (PnL per unit of volume)."""
        try:
            if not pnl_values or not volumes or len(pnl_values) != len(volumes):
                return 0.0
            
            total_pnl = sum(pnl_values)
            total_volume = sum(volumes)
            
            return total_pnl / total_volume if total_volume > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating position efficiency: {e}")
            return 0.0

    async def _check_performance_alerts(self, performance: Dict[str, Any]) -> bool:
        """Check if performance metrics trigger alerts."""
        try:
            sharpe = performance.get("sharpe_ratio", 0.0)
            drawdown = performance.get("max_drawdown", 0.0)
            total_return = performance.get("total_return", 0.0)
            volatility = performance.get("volatility", 0.0)
            
            # Check various thresholds
            if (sharpe < self.sharpe_threshold or 
                drawdown > self.drawdown_threshold or 
                total_return < -self.return_threshold or
                volatility > self.volatility_threshold):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking performance alerts: {e}")
            return False

    async def _flag_strategy(self, strategy_id: str, symbol: str, performance: Dict[str, Any]):
        """Flag underperforming strategies for review."""
        try:
            issue = {
                "type": "strategy_flagged",
                "strategy_id": strategy_id,
                "symbol": symbol,
                "sharpe_ratio": performance.get("sharpe_ratio", 0.0),
                "max_drawdown": performance.get("max_drawdown", 0.0),
                "total_return": performance.get("total_return", 0.0),
                "volatility": performance.get("volatility", 0.0),
                "timestamp": int(time.time()),
                "description": f"Flagged {strategy_id} for {symbol}: Sharpe {performance.get('sharpe_ratio', 0.0):.2f}, Drawdown {performance.get('max_drawdown', 0.0):.2f}"
            }
            
            # Store alert
            self.alert_history.append(issue)
            
            # Store alert with proper JSON serialization
            try:
                import json
                self.redis_conn.set(
                    f"strategy_engine:performance_alert:{strategy_id}:{int(time.time())}", 
                    json.dumps(issue), 
                    ex=604800
                )
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing performance alert: {e}")
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing performance alert: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error storing performance alert: {e}")
            
            self.logger.warning(f"Performance alert: {issue['description']}")
            self.stats["performance_alerts"] += 1
            
            # Notify core
            await self.notify_core(issue)
            
        except Exception as e:
            self.logger.error(f"Error flagging strategy: {e}")

    async def _store_performance_metrics(self, strategy_id: str, performance: Dict[str, Any]):
        """Store performance metrics in Redis."""
        try:
            if not isinstance(performance, dict):
                self.logger.error(f"Invalid performance type: {type(performance)}, expected dict")
                return
                
            # Store current metrics with proper JSON serialization
            try:
                import json
                self.redis_conn.set(
                    f"strategy_engine:performance:{strategy_id}", 
                    json.dumps(performance), 
                    ex=604800
                )
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing performance metrics: {e}")
                return
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing performance metrics: {e}")
                return
            except Exception as e:
                self.logger.error(f"Unexpected error storing performance metrics: {e}")
                return
            
            # Add to history
            history_key = f"strategy_engine:performance_history:{strategy_id}"
            current_history = await self._get_strategy_history(strategy_id)
            current_history.append(performance)
            
            # Keep only last 100 entries
            if len(current_history) > 100:
                current_history = current_history[-100:]
            
            # Store history with proper JSON serialization
            try:
                self.redis_conn.set(
                    history_key, 
                    json.dumps(current_history), 
                    ex=604800
                )
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing performance history: {e}")
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing performance history: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error storing performance history: {e}")
            
        except Exception as e:
            self.logger.error(f"Unexpected error in _store_performance_metrics: {e}")

    async def get_strategy_performance(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get performance metrics for a specific strategy."""
        try:
            if not isinstance(strategy_id, str):
                self.logger.error(f"Invalid strategy_id type: {type(strategy_id)}, expected string")
                return None
                
            performance_key = f"strategy_engine:performance:{strategy_id}"
            performance_data = self.redis_conn.get(performance_key)
            
            if performance_data:
                import json
                try:
                    # Handle both string and bytes responses from Redis
                    if isinstance(performance_data, bytes):
                        performance_data = performance_data.decode('utf-8')
                    elif not isinstance(performance_data, str):
                        self.logger.warning(f"Invalid performance data type: {type(performance_data)}")
                        return None
                        
                    parsed_data = json.loads(performance_data)
                    if isinstance(parsed_data, dict):
                        return parsed_data
                    else:
                        self.logger.warning(f"Invalid performance data format: expected dict, got {type(parsed_data)}")
                        return None
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON decode error for strategy performance: {e}")
                    return None
                except Exception as e:
                    self.logger.error(f"Unexpected error parsing strategy performance: {e}")
                    return None
            
            return None
            
        except ConnectionError as e:
            self.logger.error(f"Redis connection error getting strategy performance: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error getting strategy performance: {e}")
            return None

    async def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Get all performance alerts."""
        try:
            return self.alert_history.copy()
        except Exception as e:
            self.logger.error(f"Error getting performance alerts: {e}")
            return []

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance tracker statistics."""
        return {
            **self.stats,
            "uptime": time.time() - self.stats["start_time"]
        }

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of performance metrics."""
        try:
            if not isinstance(issue, dict):
                self.logger.error(f"Invalid issue type: {type(issue)}, expected dict")
                return
                
            self.logger.info(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
            
            # Publish with proper JSON serialization
            try:
                import json
                self.redis_conn.publish("strategy_engine_output", json.dumps(issue))
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error notifying core: {e}")
                self.stats["errors"] += 1
            except ConnectionError as e:
                self.logger.error(f"Redis connection error notifying core: {e}")
                self.stats["errors"] += 1
            except Exception as e:
                self.logger.error(f"Unexpected error notifying core: {e}")
                self.stats["errors"] += 1
                
        except Exception as e:
            self.logger.error(f"Unexpected error in notify_core: {e}")
            self.stats["errors"] += 1