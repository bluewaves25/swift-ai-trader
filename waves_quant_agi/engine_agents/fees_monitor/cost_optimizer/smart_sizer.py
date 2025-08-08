import time
from typing import Dict, Any
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache
from ..broker_fee_models.model_loader import ModelLoader

class SmartSizer:
    """Smart position sizing to minimize fee impact while maintaining trade effectiveness."""
    
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache, model_loader: ModelLoader):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.model_loader = model_loader
        self.max_fee_impact = config.get("max_fee_impact", 0.01)  # 1% of trade value
        self.min_position_size = config.get("min_position_size", 0.001)  # Minimum position size
        self.max_position_size = config.get("max_position_size", 1000000.0)  # Maximum position size

    async def optimize_position_size(self, trade: Dict[str, Any]) -> float:
        """Adjust position size to minimize fee impact while maintaining effectiveness."""
        try:
            broker = trade.get("broker", "unknown")
            symbol = trade.get("symbol", "unknown")
            original_size = float(trade.get("size", 1.0))
            price = float(trade.get("price", 0.0))
            
            if price <= 0:
                self.logger.log_error(f"Invalid price for {symbol}: {price}")
                return original_size

            # Get fee model for broker
            fee_model = self.model_loader.get_fee_model(broker)
            if not fee_model:
                self.logger.log(f"No fee model for {broker}, using default size")
                return original_size

            # Calculate fee impact
            commission_rate = float(fee_model.get("fees", {}).get("commission", 0.0))
            trade_value = price * original_size
            
            if trade_value <= 0:
                self.logger.log_error(f"Invalid trade value for {symbol}: {trade_value}")
                return original_size

            fee_impact = (commission_rate * trade_value) / trade_value
            
            # If fee impact is acceptable, return original size
            if fee_impact <= self.max_fee_impact:
                self.logger.log_metric("fee_impact_acceptable", fee_impact, {"symbol": symbol, "broker": broker})
                return original_size

            # Calculate optimal size to meet fee impact target
            optimal_size = original_size * (self.max_fee_impact / fee_impact)
            
            # Apply size constraints
            optimal_size = max(self.min_position_size, min(optimal_size, self.max_position_size))
            
            # Log the adjustment
            adjustment_ratio = optimal_size / original_size
            self.logger.log_metric("position_size_adjustment_ratio", adjustment_ratio, {
                "symbol": symbol, 
                "broker": broker,
                "original_size": original_size,
                "optimal_size": optimal_size
            })
            
            # Store incident for monitoring
            issue = {
                "type": "position_size_adjusted",
                "broker": broker,
                "symbol": symbol,
                "original_size": original_size,
                "adjusted_size": optimal_size,
                "adjustment_ratio": adjustment_ratio,
                "fee_impact_before": fee_impact,
                "fee_impact_after": self.max_fee_impact,
                "timestamp": int(time.time()),
                "description": f"Adjusted position size for {broker}/{symbol} from {original_size} to {optimal_size} (ratio: {adjustment_ratio:.4f})"
            }
            
            self.logger.log_issue(issue)
            self.cache.store_incident(issue)
            
            # Notify core agent
            await self.notify_core(issue)
            
            return optimal_size
            
        except Exception as e:
            self.logger.log_error(f"Error optimizing position size: {e}", {
                "trade": trade,
                "config": self.config
            })
            
            error_incident = {
                "type": "smart_sizer_error",
                "timestamp": int(time.time()),
                "description": f"Error optimizing position size: {str(e)}",
                "trade_data": trade
            }
            
            self.cache.store_incident(error_incident)
            return trade.get("size", 1.0)

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of size adjustments."""
        try:
            self.logger.log_action("notify_core", {
                "issue_type": issue.get("type"),
                "symbol": issue.get("symbol"),
                "broker": issue.get("broker"),
                "adjustment_ratio": issue.get("adjustment_ratio")
            })
            
            # Publish to Redis for real-time monitoring
            if hasattr(self.logger, 'redis_client') and self.logger.redis_client:
                try:
                    self.logger.redis_client.publish(
                        "fees_monitor:core_notifications",
                        f"position_size_adjusted:{issue.get('symbol')}:{issue.get('broker')}:{issue.get('adjustment_ratio', 0):.4f}"
                    )
                except Exception as e:
                    self.logger.log_error(f"Failed to publish to Redis: {e}")
                    
        except Exception as e:
            self.logger.log_error(f"Error notifying core: {e}")

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get statistics about position size optimizations."""
        try:
            recent_incidents = self.cache.get_recent_incidents(24)  # Last 24 hours
            adjustments = [inc for inc in recent_incidents if inc.get("type") == "position_size_adjusted"]
            
            if not adjustments:
                return {
                    "total_adjustments": 0,
                    "average_adjustment_ratio": 1.0,
                    "brokers_adjusted": [],
                    "symbols_adjusted": []
                }
            
            adjustment_ratios = [adj.get("adjustment_ratio", 1.0) for adj in adjustments]
            brokers = list(set(adj.get("broker") for adj in adjustments))
            symbols = list(set(adj.get("symbol") for adj in adjustments))
            
            return {
                "total_adjustments": len(adjustments),
                "average_adjustment_ratio": sum(adjustment_ratios) / len(adjustment_ratios),
                "min_adjustment_ratio": min(adjustment_ratios),
                "max_adjustment_ratio": max(adjustment_ratios),
                "brokers_adjusted": brokers,
                "symbols_adjusted": symbols,
                "time_period_hours": 24
            }
            
        except Exception as e:
            self.logger.log_error(f"Error getting optimization stats: {e}")
            return {
                "total_adjustments": 0,
                "average_adjustment_ratio": 1.0,
                "brokers_adjusted": [],
                "symbols_adjusted": [],
                "error": str(e)
            }