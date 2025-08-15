#!/usr/bin/env python3
"""
Slippage Manager - Execution Slippage Control
Provides comprehensive slippage management and monitoring for trade execution.
"""

import time
import asyncio
from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from ...shared_utils import get_shared_logger

class SlippageType(Enum):
    """Types of slippage."""
    POSITIVE = "positive"      # Better than expected price
    NEGATIVE = "negative"      # Worse than expected price
    ZERO = "zero"              # No slippage

class SlippageAlert:
    """Slippage alert with details."""
    
    def __init__(self, symbol: str, order_id: str, expected_price: float, 
                 actual_price: float, slippage_amount: float, slippage_type: SlippageType):
        self.symbol = symbol
        self.order_id = order_id
        self.expected_price = expected_price
        self.actual_price = actual_price
        self.slippage_amount = slippage_amount
        self.slippage_type = slippage_type
        self.timestamp = time.time()
        self.acknowledged = False

class SlippageManager:
    """Manages slippage monitoring and control for trade execution."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("execution", "slippage_manager")
        
        # Slippage configuration
        self.max_allowed_slippage = config.get("max_allowed_slippage", 0.001)  # 0.1%
        self.slippage_alert_threshold = config.get("slippage_alert_threshold", 0.0005)  # 0.05%
        self.slippage_monitoring_enabled = config.get("slippage_monitoring_enabled", True)
        
        # Slippage tracking
        self.slippage_history: List[Dict[str, Any]] = []
        self.active_alerts: List[SlippageAlert] = []
        self.slippage_stats = {
            "total_trades": 0,
            "positive_slippage_count": 0,
            "negative_slippage_count": 0,
            "zero_slippage_count": 0,
            "total_positive_slippage": 0.0,
            "total_negative_slippage": 0.0,
            "max_positive_slippage": 0.0,
            "max_negative_slippage": 0.0,
            "start_time": time.time()
        }
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_task = None
        
        self.logger.info("Slippage Manager initialized")
    
    async def start_monitoring(self):
        """Start slippage monitoring."""
        if not self.slippage_monitoring_enabled or self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Slippage monitoring started")
    
    async def stop_monitoring(self):
        """Stop slippage monitoring."""
        self.is_monitoring = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Slippage monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                # Check for slippage alerts
                await self._check_slippage_alerts()
                
                # Clean up old alerts
                await self._cleanup_old_alerts()
                
                await asyncio.sleep(1.0)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Error in slippage monitoring loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _check_slippage_alerts(self):
        """Check for slippage alerts."""
        try:
            for alert in self.active_alerts:
                if not alert.acknowledged:
                    # Check if slippage exceeds alert threshold
                    if abs(alert.slippage_amount) > self.slippage_alert_threshold:
                        self.logger.warning(
                            f"Slippage alert: {alert.symbol} order {alert.order_id} "
                            f"has {alert.slippage_type.value} slippage of {alert.slippage_amount:.6f}"
                        )
        
        except Exception as e:
            self.logger.error(f"Error checking slippage alerts: {e}")
    
    async def _cleanup_old_alerts(self):
        """Clean up old acknowledged alerts."""
        try:
            current_time = time.time()
            self.active_alerts = [
                alert for alert in self.active_alerts
                if not alert.acknowledged or (current_time - alert.timestamp) < 3600  # Keep for 1 hour
            ]
        except Exception as e:
            self.logger.error(f"Error cleaning up old alerts: {e}")
    
    def calculate_slippage(self, expected_price: float, actual_price: float) -> Tuple[float, SlippageType]:
        """Calculate slippage amount and type."""
        try:
            if expected_price == 0:
                return 0.0, SlippageType.ZERO
            
            slippage_amount = (actual_price - expected_price) / expected_price
            slippage_type = SlippageType.ZERO
            
            if slippage_amount > 0:
                slippage_type = SlippageType.POSITIVE
            elif slippage_amount < 0:
                slippage_type = SlippageType.NEGATIVE
            
            return slippage_amount, slippage_type
        
        except Exception as e:
            self.logger.error(f"Error calculating slippage: {e}")
            return 0.0, SlippageType.ZERO
    
    def record_slippage(self, symbol: str, order_id: str, expected_price: float, 
                        actual_price: float, order_size: float = 0.0):
        """Record slippage for a trade."""
        try:
            slippage_amount, slippage_type = self.calculate_slippage(expected_price, actual_price)
            
            # Create slippage record
            slippage_record = {
                "symbol": symbol,
                "order_id": order_id,
                "expected_price": expected_price,
                "actual_price": actual_price,
                "slippage_amount": slippage_amount,
                "slippage_type": slippage_type.value,
                "order_size": order_size,
                "timestamp": time.time()
            }
            
            # Add to history
            self.slippage_history.append(slippage_record)
            
            # Update statistics
            self._update_slippage_stats(slippage_amount, slippage_type)
            
            # Check if slippage exceeds maximum allowed
            if abs(slippage_amount) > self.max_allowed_slippage:
                self.logger.warning(
                    f"Slippage exceeds maximum allowed: {symbol} order {order_id} "
                    f"has slippage of {slippage_amount:.6f} (max: {self.max_allowed_slippage:.6f})"
                )
            
            # Create alert if slippage is significant
            if abs(slippage_amount) > self.slippage_alert_threshold:
                alert = SlippageAlert(
                    symbol=symbol,
                    order_id=order_id,
                    expected_price=expected_price,
                    actual_price=actual_price,
                    slippage_amount=slippage_amount,
                    slippage_type=slippage_type
                )
                self.active_alerts.append(alert)
            
            # Keep only last 1000 records to prevent memory bloat
            if len(self.slippage_history) > 1000:
                self.slippage_history.pop(0)
            
            self.logger.debug(f"Recorded slippage: {symbol} {order_id} {slippage_amount:.6f}")
        
        except Exception as e:
            self.logger.error(f"Error recording slippage: {e}")
    
    def _update_slippage_stats(self, slippage_amount: float, slippage_type: SlippageType):
        """Update slippage statistics."""
        try:
            self.slippage_stats["total_trades"] += 1
            
            if slippage_type == SlippageType.POSITIVE:
                self.slippage_stats["positive_slippage_count"] += 1
                self.slippage_stats["total_positive_slippage"] += slippage_amount
                self.slippage_stats["max_positive_slippage"] = max(
                    self.slippage_stats["max_positive_slippage"], slippage_amount
                )
            elif slippage_type == SlippageType.NEGATIVE:
                self.slippage_stats["negative_slippage_count"] += 1
                self.slippage_stats["total_negative_slippage"] += abs(slippage_amount)
                self.slippage_stats["max_negative_slippage"] = max(
                    self.slippage_stats["max_negative_slippage"], abs(slippage_amount)
                )
            else:
                self.slippage_stats["zero_slippage_count"] += 1
        
        except Exception as e:
            self.logger.error(f"Error updating slippage stats: {e}")
    
    def get_slippage_summary(self) -> Dict[str, Any]:
        """Get summary of slippage statistics."""
        try:
            total_trades = self.slippage_stats["total_trades"]
            
            if total_trades == 0:
                return {
                    "total_trades": 0,
                    "average_slippage": 0.0,
                    "positive_slippage_rate": 0.0,
                    "negative_slippage_rate": 0.0,
                    "zero_slippage_rate": 0.0
                }
            
            positive_rate = self.slippage_stats["positive_slippage_count"] / total_trades
            negative_rate = self.slippage_stats["negative_slippage_count"] / total_trades
            zero_rate = self.slippage_stats["zero_slippage_count"] / total_trades
            
            total_slippage = (self.slippage_stats["total_positive_slippage"] - 
                             self.slippage_stats["total_negative_slippage"])
            average_slippage = total_slippage / total_trades
            
            return {
                "total_trades": total_trades,
                "average_slippage": average_slippage,
                "positive_slippage_rate": positive_rate,
                "negative_slippage_rate": negative_rate,
                "zero_slippage_rate": zero_rate,
                "max_positive_slippage": self.slippage_stats["max_positive_slippage"],
                "max_negative_slippage": self.slippage_stats["max_negative_slippage"],
                "uptime_hours": (time.time() - self.slippage_stats["start_time"]) / 3600
            }
        
        except Exception as e:
            self.logger.error(f"Error getting slippage summary: {e}")
            return {}
    
    def get_recent_slippage(self, symbol: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent slippage records."""
        try:
            recent_records = self.slippage_history[-limit:] if limit > 0 else self.slippage_history
            
            if symbol:
                return [record for record in recent_records if record["symbol"] == symbol]
            
            return recent_records
        
        except Exception as e:
            self.logger.error(f"Error getting recent slippage: {e}")
            return []
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active slippage alerts."""
        try:
            return [
                {
                    "symbol": alert.symbol,
                    "order_id": alert.order_id,
                    "expected_price": alert.expected_price,
                    "actual_price": alert.actual_price,
                    "slippage_amount": alert.slippage_amount,
                    "slippage_type": alert.slippage_type.value,
                    "timestamp": alert.timestamp
                }
                for alert in self.active_alerts if not alert.acknowledged
            ]
        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}")
            return []
    
    def acknowledge_alert(self, order_id: str):
        """Acknowledge a slippage alert."""
        try:
            for alert in self.active_alerts:
                if alert.order_id == order_id and not alert.acknowledged:
                    alert.acknowledged = True
                    self.logger.info(f"Slippage alert acknowledged: {order_id}")
                    break
        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {e}")
    
    def set_max_allowed_slippage(self, max_slippage: float):
        """Set maximum allowed slippage."""
        try:
            self.max_allowed_slippage = max_slippage
            self.logger.info(f"Maximum allowed slippage set to: {max_slippage:.6f}")
        except Exception as e:
            self.logger.error(f"Error setting max allowed slippage: {e}")
    
    def set_alert_threshold(self, threshold: float):
        """Set slippage alert threshold."""
        try:
            self.slippage_alert_threshold = threshold
            self.logger.info(f"Slippage alert threshold set to: {threshold:.6f}")
        except Exception as e:
            self.logger.error(f"Error setting alert threshold: {e}")
    
    def enable_monitoring(self, enabled: bool = True):
        """Enable or disable slippage monitoring."""
        try:
            self.slippage_monitoring_enabled = enabled
            if enabled:
                self.logger.info("Slippage monitoring enabled")
            else:
                self.logger.info("Slippage monitoring disabled")
        except Exception as e:
            self.logger.error(f"Error setting monitoring state: {e}")
    
    async def check_slippage_events(self) -> List[Dict[str, Any]]:
        """Check for new slippage events that need processing."""
        try:
            if not self.slippage_monitoring_enabled:
                return []
            
            # Return recent alerts as events
            events = []
            current_time = time.time()
            
            for alert in self.active_alerts:
                # Convert alerts to events
                event = {
                    "type": "slippage_alert",
                    "symbol": alert.symbol,
                    "order_id": alert.order_id,
                    "slippage_amount": alert.slippage_amount,
                    "slippage_type": alert.slippage_type.value,
                    "severity": "high" if abs(alert.slippage_amount) > self.max_allowed_slippage else "medium",
                    "timestamp": current_time
                }
                events.append(event)
            
            # Clear processed alerts
            self.active_alerts.clear()
            
            return events
            
        except Exception as e:
            self.logger.error(f"Error checking slippage events: {e}")
            return []
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            await self.stop_monitoring()
            self.logger.info("Slippage Manager cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
