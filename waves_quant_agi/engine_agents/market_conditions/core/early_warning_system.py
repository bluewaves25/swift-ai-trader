#!/usr/bin/env python3
"""
Early Warning System - CORE REFACTORED MODULE
Handles early warning alerts and predictions for market conditions
Separated from main agent for better manageability

REFACTORED FOR SIMPLICITY:
- Early detection of market regime changes
- Warning system for potential market stress
- Clean separation of warning logic
"""

import time
from typing import Dict, Any, List, Optional
from shared_utils import get_shared_redis, get_shared_logger

class EarlyWarningSystem:
    """
    Early warning system for market conditions - detects problems before they fully manifest.
    Separated from main agent for better code organization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_conn = get_shared_redis()
        self.logger = get_shared_logger("market_conditions", "early_warning")
        
        # Warning system state
        self.warning_stats = {
            "warnings_issued": 0,
            "regime_changes_predicted": 0,
            "stress_warnings": 0,
            "flash_crash_warnings": 0,
            "accuracy_rate": 0.0
        }
        
        # Warning thresholds
        self.warning_thresholds = {
            "volatility_spike": 0.06,      # 6% volatility spike
            "volume_surge": 3.0,           # 3x volume surge
            "correlation_breakdown": 0.7,   # 70% correlation change
            "liquidity_crisis": 0.2,       # 20% liquidity remaining
            "flash_crash_precursor": 0.8   # 80% crash probability
        }
        
        # Current warning state
        self.active_warnings = {}
        self.warning_history = []
        self.last_warning_time = 0
        
        # Minimum time between warnings (prevent spam)
        self.min_warning_interval = config.get("min_warning_interval", 30)  # 30 seconds
        
    async def evaluate_warnings(self, market_data: Dict[str, Any], 
                               anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluate if early warnings should be issued based on market data and anomalies.
        """
        warnings = []
        current_time = time.time()
        
        try:
            # Check minimum interval between warnings
            if current_time - self.last_warning_time < self.min_warning_interval:
                return []
            
            # Evaluate different warning types
            volatility_warnings = await self._evaluate_volatility_warnings(market_data)
            regime_warnings = await self._evaluate_regime_warnings(market_data, anomalies)
            stress_warnings = await self._evaluate_stress_warnings(market_data, anomalies)
            flash_crash_warnings = await self._evaluate_flash_crash_warnings(market_data, anomalies)
            
            # Combine all warnings
            all_warnings = volatility_warnings + regime_warnings + stress_warnings + flash_crash_warnings
            
            # Filter and prioritize warnings
            significant_warnings = await self._filter_significant_warnings(all_warnings)
            
            # Issue warnings if any are significant
            if significant_warnings:
                await self._issue_warnings(significant_warnings)
                self.last_warning_time = current_time
                self.warning_stats["warnings_issued"] += len(significant_warnings)
            
            return significant_warnings
            
        except Exception as e:
            self.logger.error(f"Error evaluating warnings: {e}")
            return []
    
    async def _evaluate_volatility_warnings(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate volatility-based early warnings."""
        warnings = []
        
        try:
            current_volatility = market_data.get("volatility", 0)
            volatility_trend = market_data.get("volatility_trend", 0)
            
            # Check for volatility spike warning
            if current_volatility > self.warning_thresholds["volatility_spike"]:
                warning = {
                    "type": "volatility_spike_warning",
                    "severity": "high",
                    "message": f"High volatility detected: {current_volatility*100:.1f}%",
                    "probability": min(1.0, current_volatility / self.warning_thresholds["volatility_spike"]),
                    "timestamp": time.time(),
                    "details": {
                        "current_volatility": current_volatility,
                        "threshold": self.warning_thresholds["volatility_spike"],
                        "trend": volatility_trend
                    }
                }
                warnings.append(warning)
            
            # Check for volatility surge trend (early indicator)
            if volatility_trend > 0.02:  # 2% increasing trend
                warning = {
                    "type": "volatility_surge_warning",
                    "severity": "medium",
                    "message": f"Volatility surge trend detected: +{volatility_trend*100:.1f}%",
                    "probability": min(1.0, volatility_trend / 0.02),
                    "timestamp": time.time(),
                    "details": {
                        "volatility_trend": volatility_trend,
                        "current_volatility": current_volatility
                    }
                }
                warnings.append(warning)
                
        except Exception as e:
            self.logger.warning(f"Error evaluating volatility warnings: {e}")
            
        return warnings
    
    async def _evaluate_regime_warnings(self, market_data: Dict[str, Any], 
                                      anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate market regime change warnings."""
        warnings = []
        
        try:
            # Count different types of anomalies
            anomaly_counts = {}
            for anomaly in anomalies:
                anomaly_type = anomaly.get("type", "unknown")
                anomaly_counts[anomaly_type] = anomaly_counts.get(anomaly_type, 0) + 1
            
            # Check for multiple anomalies (regime change indicator)
            total_anomalies = len(anomalies)
            
            if total_anomalies >= 3:  # Multiple anomalies suggest regime change
                warning = {
                    "type": "regime_change_warning",
                    "severity": "critical" if total_anomalies >= 5 else "high",
                    "message": f"Potential regime change: {total_anomalies} anomalies detected",
                    "probability": min(1.0, total_anomalies / 10.0),
                    "timestamp": time.time(),
                    "details": {
                        "total_anomalies": total_anomalies,
                        "anomaly_types": list(anomaly_counts.keys()),
                        "anomaly_counts": anomaly_counts
                    }
                }
                warnings.append(warning)
                self.warning_stats["regime_changes_predicted"] += 1
            
            # Check for correlation breakdown (regime indicator)
            correlation_anomalies = anomaly_counts.get("correlation_anomaly", 0)
            if correlation_anomalies >= 2:
                warning = {
                    "type": "correlation_breakdown_warning",
                    "severity": "high",
                    "message": f"Correlation structure breaking down: {correlation_anomalies} instances",
                    "probability": min(1.0, correlation_anomalies / 5.0),
                    "timestamp": time.time(),
                    "details": {
                        "correlation_anomalies": correlation_anomalies,
                        "threshold": self.warning_thresholds["correlation_breakdown"]
                    }
                }
                warnings.append(warning)
                
        except Exception as e:
            self.logger.warning(f"Error evaluating regime warnings: {e}")
            
        return warnings
    
    async def _evaluate_stress_warnings(self, market_data: Dict[str, Any], 
                                      anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate market stress warnings."""
        warnings = []
        
        try:
            # Calculate market stress indicators
            volatility = market_data.get("volatility", 0)
            volume_ratio = market_data.get("volume_ratio", 1.0)
            liquidity_ratio = market_data.get("liquidity_ratio", 1.0)
            
            # Composite stress score
            stress_score = (
                volatility * 2.0 +  # Volatility weight
                max(0, volume_ratio - 1.0) * 0.5 +  # Excess volume
                max(0, 1.0 - liquidity_ratio) * 3.0  # Liquidity shortage
            )
            
            # Check for market stress
            if stress_score > 0.3:  # Stress threshold
                warning = {
                    "type": "market_stress_warning",
                    "severity": "critical" if stress_score > 0.6 else "high",
                    "message": f"Market stress detected: score {stress_score:.2f}",
                    "probability": min(1.0, stress_score / 0.6),
                    "timestamp": time.time(),
                    "details": {
                        "stress_score": stress_score,
                        "volatility": volatility,
                        "volume_ratio": volume_ratio,
                        "liquidity_ratio": liquidity_ratio
                    }
                }
                warnings.append(warning)
                self.warning_stats["stress_warnings"] += 1
            
            # Check for liquidity crisis
            if liquidity_ratio < self.warning_thresholds["liquidity_crisis"]:
                warning = {
                    "type": "liquidity_crisis_warning",
                    "severity": "critical",
                    "message": f"Liquidity crisis warning: {liquidity_ratio*100:.1f}% remaining",
                    "probability": 1.0 - liquidity_ratio,
                    "timestamp": time.time(),
                    "details": {
                        "liquidity_ratio": liquidity_ratio,
                        "threshold": self.warning_thresholds["liquidity_crisis"]
                    }
                }
                warnings.append(warning)
                
        except Exception as e:
            self.logger.warning(f"Error evaluating stress warnings: {e}")
            
        return warnings
    
    async def _evaluate_flash_crash_warnings(self, market_data: Dict[str, Any], 
                                           anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate flash crash precursor warnings."""
        warnings = []
        
        try:
            # Flash crash indicators
            price_velocity = market_data.get("price_velocity", 0)  # Rate of price change
            order_book_imbalance = market_data.get("order_imbalance", 0)
            liquidity_ratio = market_data.get("liquidity_ratio", 1.0)
            volatility = market_data.get("volatility", 0)
            
            # Flash crash probability calculation
            flash_crash_probability = (
                abs(price_velocity) * 10.0 +  # Rapid price movement
                abs(order_book_imbalance) * 5.0 +  # Order imbalance
                max(0, 1.0 - liquidity_ratio) * 3.0 +  # Low liquidity
                volatility * 2.0  # High volatility
            )
            
            # Normalize to 0-1 range
            flash_crash_probability = min(1.0, flash_crash_probability / 10.0)
            
            # Check for flash crash precursors
            if flash_crash_probability > self.warning_thresholds["flash_crash_precursor"]:
                warning = {
                    "type": "flash_crash_precursor_warning",
                    "severity": "critical",
                    "message": f"Flash crash precursors detected: {flash_crash_probability*100:.1f}% probability",
                    "probability": flash_crash_probability,
                    "timestamp": time.time(),
                    "details": {
                        "flash_crash_probability": flash_crash_probability,
                        "price_velocity": price_velocity,
                        "order_imbalance": order_book_imbalance,
                        "liquidity_ratio": liquidity_ratio,
                        "volatility": volatility
                    }
                }
                warnings.append(warning)
                self.warning_stats["flash_crash_warnings"] += 1
                
        except Exception as e:
            self.logger.warning(f"Error evaluating flash crash warnings: {e}")
            
        return warnings
    
    async def _filter_significant_warnings(self, warnings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and prioritize significant warnings."""
        
        if not warnings:
            return []
        
        # Sort by severity and probability
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        
        sorted_warnings = sorted(
            warnings,
            key=lambda x: (
                severity_order.get(x.get("severity", "low"), 0),
                x.get("probability", 0)
            ),
            reverse=True
        )
        
        # Take top warnings to avoid alert fatigue
        max_warnings = self.config.get("max_warnings_per_evaluation", 3)
        significant_warnings = sorted_warnings[:max_warnings]
        
        return significant_warnings
    
    async def _issue_warnings(self, warnings: List[Dict[str, Any]]):
        """Issue warnings to the system."""
        
        for warning in warnings:
            try:
                # Store warning in Redis
                warning_key = f"warning:{warning['type']}:{int(time.time())}"
                self.redis_conn.set(warning_key, warning, expire=3600)  # 1 hour expiration
                
                # Add to active warnings
                self.active_warnings[warning["type"]] = warning
                
                # Add to history
                self.warning_history.append(warning)
                if len(self.warning_history) > 100:  # Keep last 100 warnings
                    self.warning_history.pop(0)
                
                # Publish warning to communication system
                await self._publish_warning(warning)
                
                # Log the warning
                self.logger.warning(f"EARLY WARNING: {warning['message']}")
                
            except Exception as e:
                self.logger.error(f"Error issuing warning: {e}")
    
    async def _publish_warning(self, warning: Dict[str, Any]):
        """Publish warning to the communication system."""
        try:
            warning_message = {
                "type": "MARKET_ANOMALY_ALERT",
                "warning": warning,
                "timestamp": time.time(),
                "source": "market_conditions_early_warning"
            }
            
            # Publish to Redis channel for other agents
            self.redis_conn.publish("market_warnings", warning_message)
            
        except Exception as e:
            self.logger.warning(f"Error publishing warning: {e}")
    
    def get_warning_stats(self) -> Dict[str, Any]:
        """Get warning system statistics."""
        return {
            **self.warning_stats,
            "active_warnings_count": len(self.active_warnings),
            "warning_history_count": len(self.warning_history),
            "last_warning_minutes_ago": (time.time() - self.last_warning_time) / 60 if self.last_warning_time else 0,
            "current_thresholds": self.warning_thresholds
        }
    
    def get_active_warnings(self) -> Dict[str, Any]:
        """Get currently active warnings."""
        # Filter out old warnings (older than 1 hour)
        current_time = time.time()
        active_warnings = {}
        
        for warning_type, warning in self.active_warnings.items():
            if current_time - warning.get("timestamp", 0) < 3600:  # 1 hour
                active_warnings[warning_type] = warning
        
        # Update active warnings
        self.active_warnings = active_warnings
        
        return active_warnings
    
    def clear_warning(self, warning_type: str):
        """Clear a specific warning type."""
        if warning_type in self.active_warnings:
            del self.active_warnings[warning_type]
            self.logger.info(f"Cleared warning: {warning_type}")
    
    def adjust_thresholds(self, threshold_adjustments: Dict[str, float]):
        """Adjust warning thresholds."""
        for threshold_type, adjustment in threshold_adjustments.items():
            if threshold_type in self.warning_thresholds:
                self.warning_thresholds[threshold_type] = adjustment
        
        self.logger.info(f"Adjusted warning thresholds: {threshold_adjustments}")
    
    def reset_stats(self):
        """Reset warning statistics."""
        self.warning_stats = {
            "warnings_issued": 0,
            "regime_changes_predicted": 0,
            "stress_warnings": 0,
            "flash_crash_warnings": 0,
            "accuracy_rate": 0.0
        }
