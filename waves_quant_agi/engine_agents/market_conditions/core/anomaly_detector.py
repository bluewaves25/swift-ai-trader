#!/usr/bin/env python3
"""
Anomaly Detector - CORE REFACTORED MODULE
Handles wide anomaly detection and early warning systems
Separated from main agent for better manageability

REFACTORED FOR SIMPLICITY:
- Wide market scanning for strange behaviors
- Early warning system for market anomalies
- Clean separation of detection logic
"""

import time
from typing import Dict, Any, List, Optional, Tuple
from shared_utils import get_shared_logger, get_agent_learner, LearningType

class AnomalyDetector:
    """
    Core anomaly detection engine - handles wide market scanning.
    Separated from main agent for better code organization.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("market_conditions", "anomaly_detector")
        self.learner = get_agent_learner("market_conditions", LearningType.MARKET_PREDICTION, 8)
        
        # Anomaly detection state
        self.detection_stats = {
            "total_scans": 0,
            "anomalies_detected": 0,
            "early_warnings_issued": 0,
            "false_positives": 0,
            "detection_accuracy": 0.0
        }
        
        # Anomaly thresholds (simplified but effective)
        self.thresholds = {
            "price_anomaly": 0.05,      # 5% sudden price change
            "volume_anomaly": 2.0,      # 2x normal volume
            "volatility_anomaly": 3.0,  # 3x normal volatility
            "correlation_anomaly": 0.8, # 80% correlation break
            "liquidity_anomaly": 0.3    # 30% liquidity drop
        }
        
        # Current market baseline (for anomaly comparison)
        self.market_baseline = {
            "normal_volatility": 0.02,
            "normal_volume": 1000000,
            "normal_spread": 0.001,
            "normal_correlation": 0.3,
            "normal_liquidity": 1.0
        }
        
    async def scan_for_anomalies(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Perform wide anomaly scan across all market aspects.
        This is the main method for detecting strange behaviors.
        """
        start_time = time.time()
        anomalies = []
        
        try:
            self.detection_stats["total_scans"] += 1
            
            # Scan different types of anomalies
            price_anomalies = await self._detect_price_anomalies(market_data)
            volume_anomalies = await self._detect_volume_anomalies(market_data)
            volatility_anomalies = await self._detect_volatility_anomalies(market_data)
            correlation_anomalies = await self._detect_correlation_anomalies(market_data)
            liquidity_anomalies = await self._detect_liquidity_anomalies(market_data)
            
            # Combine all anomalies
            all_anomalies = (
                price_anomalies + volume_anomalies + volatility_anomalies + 
                correlation_anomalies + liquidity_anomalies
            )
            
            # Filter and prioritize anomalies
            significant_anomalies = await self._filter_significant_anomalies(all_anomalies)
            
            # Learn from detection patterns
            await self._learn_from_detection(market_data, significant_anomalies, start_time)
            
            # Update statistics
            self.detection_stats["anomalies_detected"] += len(significant_anomalies)
            
            return significant_anomalies
            
        except Exception as e:
            self.logger.error(f"Error in anomaly scan: {e}")
            return []
    
    async def _detect_price_anomalies(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect unusual price movements."""
        anomalies = []
        
        try:
            current_price = market_data.get("price", 0)
            previous_price = market_data.get("previous_price", current_price)
            
            if previous_price > 0:
                price_change = abs(current_price - previous_price) / previous_price
                
                if price_change > self.thresholds["price_anomaly"]:
                    anomaly = {
                        "type": "price_anomaly",
                        "severity": "high" if price_change > self.thresholds["price_anomaly"] * 2 else "medium",
                        "description": f"Unusual price movement: {price_change*100:.1f}%",
                        "value": price_change,
                        "symbol": market_data.get("symbol", "UNKNOWN"),
                        "timestamp": time.time(),
                        "details": {
                            "current_price": current_price,
                            "previous_price": previous_price,
                            "change_percent": price_change * 100
                        }
                    }
                    anomalies.append(anomaly)
                    
        except Exception as e:
            self.logger.warning(f"Error detecting price anomalies: {e}")
            
        return anomalies
    
    async def _detect_volume_anomalies(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect unusual volume patterns."""
        anomalies = []
        
        try:
            current_volume = market_data.get("volume", 0)
            average_volume = market_data.get("average_volume", self.market_baseline["normal_volume"])
            
            if average_volume > 0:
                volume_ratio = current_volume / average_volume
                
                if volume_ratio > self.thresholds["volume_anomaly"]:
                    anomaly = {
                        "type": "volume_anomaly", 
                        "severity": "high" if volume_ratio > self.thresholds["volume_anomaly"] * 2 else "medium",
                        "description": f"Unusual volume spike: {volume_ratio:.1f}x normal",
                        "value": volume_ratio,
                        "symbol": market_data.get("symbol", "UNKNOWN"),
                        "timestamp": time.time(),
                        "details": {
                            "current_volume": current_volume,
                            "average_volume": average_volume,
                            "volume_ratio": volume_ratio
                        }
                    }
                    anomalies.append(anomaly)
                    
        except Exception as e:
            self.logger.warning(f"Error detecting volume anomalies: {e}")
            
        return anomalies
    
    async def _detect_volatility_anomalies(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect unusual volatility patterns."""
        anomalies = []
        
        try:
            current_volatility = market_data.get("volatility", 0)
            normal_volatility = self.market_baseline["normal_volatility"]
            
            volatility_ratio = current_volatility / normal_volatility if normal_volatility > 0 else 0
            
            if volatility_ratio > self.thresholds["volatility_anomaly"]:
                anomaly = {
                    "type": "volatility_anomaly",
                    "severity": "critical" if volatility_ratio > self.thresholds["volatility_anomaly"] * 2 else "high",
                    "description": f"Extreme volatility: {volatility_ratio:.1f}x normal",
                    "value": volatility_ratio,
                    "symbol": market_data.get("symbol", "UNKNOWN"),
                    "timestamp": time.time(),
                    "details": {
                        "current_volatility": current_volatility,
                        "normal_volatility": normal_volatility,
                        "volatility_ratio": volatility_ratio
                    }
                }
                anomalies.append(anomaly)
                
        except Exception as e:
            self.logger.warning(f"Error detecting volatility anomalies: {e}")
            
        return anomalies
    
    async def _detect_correlation_anomalies(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect unusual correlation breakdowns."""
        anomalies = []
        
        try:
            correlations = market_data.get("correlations", {})
            
            for asset_pair, correlation in correlations.items():
                expected_correlation = market_data.get("expected_correlations", {}).get(asset_pair, 0.3)
                correlation_change = abs(correlation - expected_correlation)
                
                if correlation_change > self.thresholds["correlation_anomaly"]:
                    anomaly = {
                        "type": "correlation_anomaly",
                        "severity": "medium",
                        "description": f"Correlation breakdown in {asset_pair}: {correlation:.2f}",
                        "value": correlation_change,
                        "symbol": asset_pair,
                        "timestamp": time.time(),
                        "details": {
                            "current_correlation": correlation,
                            "expected_correlation": expected_correlation,
                            "correlation_change": correlation_change
                        }
                    }
                    anomalies.append(anomaly)
                    
        except Exception as e:
            self.logger.warning(f"Error detecting correlation anomalies: {e}")
            
        return anomalies
    
    async def _detect_liquidity_anomalies(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect unusual liquidity conditions."""
        anomalies = []
        
        try:
            current_spread = market_data.get("spread", 0)
            normal_spread = self.market_baseline["normal_spread"]
            liquidity_ratio = market_data.get("liquidity_ratio", 1.0)
            
            # Check for wide spreads (liquidity problems)
            if current_spread > normal_spread * 3:  # 3x normal spread
                anomaly = {
                    "type": "liquidity_anomaly",
                    "severity": "high",
                    "description": f"Wide spread indicating low liquidity: {current_spread:.4f}",
                    "value": current_spread / normal_spread,
                    "symbol": market_data.get("symbol", "UNKNOWN"),
                    "timestamp": time.time(),
                    "details": {
                        "current_spread": current_spread,
                        "normal_spread": normal_spread,
                        "liquidity_ratio": liquidity_ratio
                    }
                }
                anomalies.append(anomaly)
            
            # Check for liquidity ratio anomalies
            if liquidity_ratio < self.thresholds["liquidity_anomaly"]:
                anomaly = {
                    "type": "liquidity_anomaly",
                    "severity": "medium",
                    "description": f"Low liquidity detected: {liquidity_ratio:.2f}",
                    "value": liquidity_ratio,
                    "symbol": market_data.get("symbol", "UNKNOWN"),
                    "timestamp": time.time(),
                    "details": {
                        "liquidity_ratio": liquidity_ratio,
                        "threshold": self.thresholds["liquidity_anomaly"]
                    }
                }
                anomalies.append(anomaly)
                
        except Exception as e:
            self.logger.warning(f"Error detecting liquidity anomalies: {e}")
            
        return anomalies
    
    async def _filter_significant_anomalies(self, anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and prioritize significant anomalies."""
        
        if not anomalies:
            return []
        
        # Sort by severity and value
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        
        sorted_anomalies = sorted(
            anomalies,
            key=lambda x: (severity_order.get(x.get("severity", "low"), 0), x.get("value", 0)),
            reverse=True
        )
        
        # Take top anomalies to avoid noise
        max_anomalies = self.config.get("max_anomalies_per_scan", 5)
        significant_anomalies = sorted_anomalies[:max_anomalies]
        
        # Add combined severity score
        for anomaly in significant_anomalies:
            anomaly["combined_score"] = self._calculate_anomaly_score(anomaly)
        
        return significant_anomalies
    
    def _calculate_anomaly_score(self, anomaly: Dict[str, Any]) -> float:
        """Calculate combined anomaly score."""
        severity_scores = {"critical": 1.0, "high": 0.7, "medium": 0.5, "low": 0.3}
        severity_score = severity_scores.get(anomaly.get("severity", "low"), 0.3)
        value_score = min(1.0, anomaly.get("value", 0) / 10.0)  # Normalize to 0-1
        
        return (severity_score + value_score) / 2
    
    async def _learn_from_detection(self, market_data: Dict[str, Any], 
                                  anomalies: List[Dict[str, Any]], start_time: float):
        """Learn from anomaly detection patterns."""
        try:
            # Create learning features from market data
            features = [
                market_data.get("price", 0) / 10000.0,  # Normalize price
                market_data.get("volume", 0) / 1000000.0,  # Normalize volume
                market_data.get("volatility", 0),
                market_data.get("spread", 0) * 1000,  # Scale spread
                len(anomalies),  # Number of anomalies detected
                time.time() - start_time,  # Detection time
                1.0 if anomalies else 0.0,  # Anomaly detected flag
                sum(1 for a in anomalies if a.get("severity") == "critical") / max(len(anomalies), 1)  # Critical ratio
            ]
            
            # Target is the anomaly severity (for learning improvement)
            if anomalies:
                target = max(self._calculate_anomaly_score(a) for a in anomalies)
            else:
                target = 0.0
            
            # Learn for future detection improvement
            from shared_utils import LearningData
            learning_data = LearningData(
                agent_name="market_conditions",
                learning_type=LearningType.MARKET_PREDICTION,
                input_features=features,
                target_value=target
            )
            
            self.learner.learn(learning_data)
            
        except Exception as e:
            self.logger.warning(f"Learning error: {e}")
    
    def update_baseline(self, market_data: Dict[str, Any]):
        """Update market baseline for anomaly detection."""
        try:
            # Simple exponential moving average update
            alpha = 0.1  # Learning rate
            
            if "volatility" in market_data:
                current_vol = market_data["volatility"]
                self.market_baseline["normal_volatility"] = (
                    (1 - alpha) * self.market_baseline["normal_volatility"] + 
                    alpha * current_vol
                )
            
            if "volume" in market_data:
                current_vol = market_data["volume"]
                self.market_baseline["normal_volume"] = (
                    (1 - alpha) * self.market_baseline["normal_volume"] + 
                    alpha * current_vol
                )
            
            if "spread" in market_data:
                current_spread = market_data["spread"]
                self.market_baseline["normal_spread"] = (
                    (1 - alpha) * self.market_baseline["normal_spread"] + 
                    alpha * current_spread
                )
                
        except Exception as e:
            self.logger.warning(f"Error updating baseline: {e}")
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get anomaly detection statistics."""
        total_scans = max(1, self.detection_stats["total_scans"])
        
        return {
            **self.detection_stats,
            "anomaly_rate": self.detection_stats["anomalies_detected"] / total_scans,
            "warning_rate": self.detection_stats["early_warnings_issued"] / total_scans,
            "accuracy": self.detection_stats["detection_accuracy"],
            "current_baseline": self.market_baseline,
            "current_thresholds": self.thresholds
        }
    
    def adjust_sensitivity(self, sensitivity_factor: float):
        """Adjust anomaly detection sensitivity."""
        for key in self.thresholds:
            self.thresholds[key] *= sensitivity_factor
        
        self.logger.info(f"Adjusted anomaly sensitivity by factor {sensitivity_factor}")
    
    def reset_stats(self):
        """Reset detection statistics."""
        self.detection_stats = {
            "total_scans": 0,
            "anomalies_detected": 0,
            "early_warnings_issued": 0,
            "false_positives": 0,
            "detection_accuracy": 0.0
        }
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            # Reset statistics
            self.reset_stats()
            
            # Clear any cached data
            self.market_baseline = {
                "normal_volatility": 0.02,
                "normal_volume": 1000000,
                "normal_spread": 0.001,
                "normal_correlation": 0.3,
                "normal_liquidity": 1.0
            }
            
            self.logger.info("AnomalyDetector cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
