#!/usr/bin/env python3
"""
Cost Analyzer - Trading Cost Analysis
Analyzes and tracks trading costs including fees, spreads, and slippage.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from ...shared_utils import get_shared_logger

class CostAnalysis:
    """Represents a cost analysis result."""
    
    def __init__(self, analysis_id: str, symbol: str, trade_type: str, 
                 timestamp: float, total_cost: float, breakdown: Dict[str, float]):
        self.analysis_id = analysis_id
        self.symbol = symbol
        self.trade_type = trade_type
        self.timestamp = timestamp
        self.total_cost = total_cost
        self.breakdown = breakdown
        self.cost_percentage = 0.0
        self.analysis_metadata = {}

class CostAnalyzer:
    """Analyzes trading costs and provides cost optimization insights."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("fees_monitor", "cost_analyzer")
        
        # Analysis configuration
        self.cost_thresholds = config.get("cost_thresholds", {
            "high_cost": 0.002,      # 0.2%
            "medium_cost": 0.001,    # 0.1%
            "low_cost": 0.0005       # 0.05%
        })
        
        self.analysis_enabled = config.get("cost_analysis_enabled", True)
        self.historical_analysis_count = config.get("historical_analysis_count", 1000)
        
        # Cost tracking
        self.cost_history: List[CostAnalysis] = []
        self.cost_statistics: Dict[str, Dict[str, Any]] = {}
        self.cost_alerts: List[Dict[str, Any]] = []
        
        # Analysis state
        self.is_analyzing = False
        self.analysis_task = None
        
        self.logger.info("Cost Analyzer initialized")
    
    async def start_analysis(self):
        """Start cost analysis monitoring."""
        if not self.analysis_enabled or self.is_analyzing:
            return
        
        self.is_analyzing = True
        self.analysis_task = asyncio.create_task(self._analysis_loop())
        self.logger.info("Cost analysis started")
    
    async def stop_analysis(self):
        """Stop cost analysis monitoring."""
        self.is_analyzing = False
        if self.analysis_task:
            self.analysis_task.cancel()
            try:
                await self.analysis_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Cost analysis stopped")
    
    async def _analysis_loop(self):
        """Main analysis loop."""
        while self.is_analyzing:
            try:
                # Analyze recent costs
                await self._analyze_recent_costs()
                
                # Generate cost insights
                await self._generate_cost_insights()
                
                # Clean up old data
                await self._cleanup_old_data()
                
                await asyncio.sleep(60.0)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in analysis loop: {e}")
                await asyncio.sleep(60.0)
    
    async def _analyze_recent_costs(self):
        """Analyze recent cost data."""
        try:
            if not self.cost_history:
                return
            
            # Get recent costs (last 100)
            recent_costs = self.cost_history[-100:] if len(self.cost_history) > 100 else self.cost_history
            
            # Analyze by symbol
            symbol_costs = {}
            for cost in recent_costs:
                symbol = cost.symbol
                if symbol not in symbol_costs:
                    symbol_costs[symbol] = []
                symbol_costs[symbol].append(cost)
            
            # Calculate statistics for each symbol
            for symbol, costs in symbol_costs.items():
                await self._calculate_symbol_statistics(symbol, costs)
                
        except Exception as e:
            self.logger.error(f"Error analyzing recent costs: {e}")
    
    async def _calculate_symbol_statistics(self, symbol: str, costs: List[CostAnalysis]):
        """Calculate cost statistics for a specific symbol."""
        try:
            if not costs:
                return
            
            total_costs = [cost.total_cost for cost in costs]
            cost_percentages = [cost.cost_percentage for cost in costs]
            
            # Calculate basic statistics
            avg_cost = sum(total_costs) / len(total_costs)
            min_cost = min(total_costs)
            max_cost = max(total_costs)
            avg_percentage = sum(cost_percentages) / len(cost_percentages)
            
            # Calculate cost trends
            recent_costs = costs[-10:] if len(costs) > 10 else costs
            if len(recent_costs) > 1:
                cost_trend = (recent_costs[-1].total_cost - recent_costs[0].total_cost) / len(recent_costs)
            else:
                cost_trend = 0.0
            
            # Store statistics
            self.cost_statistics[symbol] = {
                "total_trades": len(costs),
                "average_cost": avg_cost,
                "min_cost": min_cost,
                "max_cost": max_cost,
                "average_percentage": avg_percentage,
                "cost_trend": cost_trend,
                "last_updated": time.time(),
                "recent_costs": [cost.total_cost for cost in recent_costs[-5:]]  # Last 5 costs
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating statistics for {symbol}: {e}")
    
    async def _generate_cost_insights(self):
        """Generate cost optimization insights."""
        try:
            for symbol, stats in self.cost_statistics.items():
                avg_cost = stats.get("average_cost", 0.0)
                cost_trend = stats.get("cost_trend", 0.0)
                
                # Check for high costs
                if avg_cost > self.cost_thresholds["high_cost"]:
                    await self._create_cost_alert(symbol, "high_cost", avg_cost, "Costs are significantly high")
                
                # Check for increasing cost trends
                elif cost_trend > 0.0001:  # Costs increasing
                    await self._create_cost_alert(symbol, "increasing_trend", cost_trend, "Costs are trending upward")
                
                # Check for cost optimization opportunities
                elif avg_cost < self.cost_thresholds["low_cost"]:
                    await self._create_cost_alert(symbol, "optimization_opportunity", avg_cost, "Costs are well optimized")
                    
        except Exception as e:
            self.logger.error(f"Error generating cost insights: {e}")
    
    async def _create_cost_alert(self, symbol: str, alert_type: str, value: float, message: str):
        """Create a cost alert."""
        try:
            # Check if similar alert already exists
            existing_alert = next(
                (alert for alert in self.cost_alerts 
                 if alert.get("symbol") == symbol and alert.get("type") == alert_type), None
            )
            
            if not existing_alert:
                alert = {
                    "symbol": symbol,
                    "type": alert_type,
                    "value": value,
                    "message": message,
                    "timestamp": time.time(),
                    "acknowledged": False
                }
                
                self.cost_alerts.append(alert)
                self.logger.warning(f"Cost alert for {symbol}: {message} (value: {value:.6f})")
                
        except Exception as e:
            self.logger.error(f"Error creating cost alert: {e}")
    
    async def _cleanup_old_data(self):
        """Clean up old cost data."""
        try:
            current_time = time.time()
            max_age = 86400 * 7  # 7 days
            
            # Remove old cost history
            self.cost_history = [
                cost for cost in self.cost_history
                if (current_time - cost.timestamp) < max_age
            ]
            
            # Remove old alerts
            self.cost_alerts = [
                alert for alert in self.cost_alerts
                if (current_time - alert.get("timestamp", 0)) < max_age
            ]
            
            # Keep only recent statistics
            if len(self.cost_history) > self.historical_analysis_count:
                self.cost_history = self.cost_history[-self.historical_analysis_count:]
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    async def analyze_trade_cost(self, trade_data: Dict[str, Any]) -> CostAnalysis:
        """Analyze the cost of a specific trade."""
        try:
            symbol = trade_data.get("symbol", "unknown")
            trade_type = trade_data.get("trade_type", "unknown")
            trade_value = trade_data.get("trade_value", 0.0)
            
            # Calculate cost breakdown
            cost_breakdown = await self._calculate_cost_breakdown(trade_data)
            
            # Calculate total cost
            total_cost = sum(cost_breakdown.values())
            
            # Calculate cost percentage
            cost_percentage = (total_cost / trade_value) if trade_value > 0 else 0.0
            
            # Create cost analysis
            analysis = CostAnalysis(
                analysis_id=f"cost_{int(time.time())}_{symbol}",
                symbol=symbol,
                trade_type=trade_type,
                timestamp=time.time(),
                total_cost=total_cost,
                breakdown=cost_breakdown
            )
            analysis.cost_percentage = cost_percentage
            
            # Add to history
            self.cost_history.append(analysis)
            
            # Keep only recent history
            if len(self.cost_history) > self.historical_analysis_count:
                self.cost_history.pop(0)
            
            self.logger.info(f"Cost analysis completed for {symbol}: {total_cost:.6f} ({cost_percentage:.4%})")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing trade cost: {e}")
            return None
    
    async def _calculate_cost_breakdown(self, trade_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate detailed cost breakdown for a trade."""
        try:
            breakdown = {}
            
            # Commission costs
            commission = trade_data.get("commission", 0.0)
            breakdown["commission"] = commission
            
            # Spread costs
            spread = trade_data.get("spread", 0.0)
            breakdown["spread"] = spread
            
            # Slippage costs
            slippage = trade_data.get("slippage", 0.0)
            breakdown["slippage"] = slippage
            
            # Market impact costs
            market_impact = trade_data.get("market_impact", 0.0)
            breakdown["market_impact"] = market_impact
            
            # Other fees
            other_fees = trade_data.get("other_fees", 0.0)
            breakdown["other_fees"] = other_fees
            
            return breakdown
            
        except Exception as e:
            self.logger.error(f"Error calculating cost breakdown: {e}")
            return {}
    
    def get_cost_summary(self, symbol: str = None) -> Dict[str, Any]:
        """Get cost summary for all symbols or a specific symbol."""
        try:
            if symbol:
                return self.cost_statistics.get(symbol, {})
            
            # Aggregate summary across all symbols
            if not self.cost_statistics:
                return {"total_symbols": 0}
            
            total_symbols = len(self.cost_statistics)
            all_costs = []
            
            for stats in self.cost_statistics.values():
                all_costs.extend(stats.get("recent_costs", []))
            
            if all_costs:
                overall_avg_cost = sum(all_costs) / len(all_costs)
                overall_min_cost = min(all_costs)
                overall_max_cost = max(all_costs)
            else:
                overall_avg_cost = overall_min_cost = overall_max_cost = 0.0
            
            return {
                "total_symbols": total_symbols,
                "overall_average_cost": overall_avg_cost,
                "overall_min_cost": overall_min_cost,
                "overall_max_cost": overall_max_cost,
                "symbols_analyzed": list(self.cost_statistics.keys())
            }
            
        except Exception as e:
            self.logger.error(f"Error getting cost summary: {e}")
            return {}
    
    def get_cost_history(self, symbol: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get cost analysis history."""
        try:
            if symbol:
                filtered_history = [
                    cost for cost in self.cost_history 
                    if cost.symbol == symbol
                ]
            else:
                filtered_history = self.cost_history
            
            # Convert to dictionary format
            history = []
            for cost in filtered_history[-limit:]:
                history.append({
                    "analysis_id": cost.analysis_id,
                    "symbol": cost.symbol,
                    "trade_type": cost.trade_type,
                    "timestamp": cost.timestamp,
                    "total_cost": cost.total_cost,
                    "cost_percentage": cost.cost_percentage,
                    "breakdown": cost.breakdown
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Error getting cost history: {e}")
            return []
    
    def get_cost_alerts(self) -> List[Dict[str, Any]]:
        """Get active cost alerts."""
        try:
            return [
                alert for alert in self.cost_alerts 
                if not alert.get("acknowledged", False)
            ]
        except Exception as e:
            self.logger.error(f"Error getting cost alerts: {e}")
            return []
    
    def acknowledge_alert(self, symbol: str, alert_type: str):
        """Acknowledge a cost alert."""
        try:
            for alert in self.cost_alerts:
                if alert.get("symbol") == symbol and alert.get("type") == alert_type:
                    alert["acknowledged"] = True
                    self.logger.info(f"Cost alert acknowledged: {symbol} - {alert_type}")
                    break
        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {e}")
    
    def set_cost_thresholds(self, high_cost: float, medium_cost: float, low_cost: float):
        """Set cost thresholds for alerts."""
        try:
            self.cost_thresholds = {
                "high_cost": high_cost,
                "medium_cost": medium_cost,
                "low_cost": low_cost
            }
            self.logger.info(f"Cost thresholds updated: high={high_cost:.6f}, medium={medium_cost:.6f}, low={low_cost:.6f}")
        except Exception as e:
            self.logger.error(f"Error setting cost thresholds: {e}")
    
    def enable_analysis(self, enabled: bool = True):
        """Enable or disable cost analysis."""
        try:
            self.analysis_enabled = enabled
            self.logger.info(f"Cost analysis {'enabled' if enabled else 'disabled'}")
        except Exception as e:
            self.logger.error(f"Error setting analysis state: {e}")
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            await self.stop_analysis()
            self.cost_history.clear()
            self.cost_statistics.clear()
            self.cost_alerts.clear()
            self.logger.info("Cost Analyzer cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
