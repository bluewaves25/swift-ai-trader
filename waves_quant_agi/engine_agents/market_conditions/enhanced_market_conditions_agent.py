#!/usr/bin/env python3
"""
Enhanced Market Conditions Agent - ROLE CONSOLIDATED: MARKET ANOMALY DETECTION ONLY
Removed optimization functionality - now handled by Strategy Engine Agent.
Focuses exclusively on market anomaly detection, regime analysis, and early warning systems.
"""

import asyncio
import time
import json
from typing import Dict, Any, List
from engine_agents.shared_utils import BaseAgent, register_agent

class EnhancedMarketConditionsAgent(BaseAgent):
    """Enhanced market conditions agent - focused solely on market anomaly detection."""
    
    def _initialize_agent_components(self):
        """Initialize market conditions specific components."""
        # Initialize market conditions components
        self.anomaly_detector = None
        self.early_warning = None
        self.regime_analyzer = None
        
        # Market conditions state
        self.market_state = {
            "anomaly_level": 0.0,
            "warning_level": "normal",
            "last_scan_time": time.time(),
            "market_regime": "unknown",
            "detected_anomalies": [],
            "active_warnings": [],
            "regime_history": []
        }
        
        # Market conditions statistics
        self.stats = {
            "total_scans": 0,
            "anomalies_detected": 0,
            "warnings_issued": 0,
            "regime_changes": 0,
            "false_positives": 0,
            "start_time": time.time()
        }
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Market conditions specific startup logic."""
        try:
            # Initialize anomaly detection components
            await self._initialize_anomaly_detection()
            
            # Initialize early warning systems
            await self._initialize_early_warning()
            
            # Initialize regime analysis
            await self._initialize_regime_analysis()
            
            self.logger.info("✅ Market Conditions Agent: Anomaly detection systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error in market conditions startup: {e}")
            raise
    
    async def _agent_specific_shutdown(self):
        """Market conditions specific shutdown logic."""
        try:
            # Cleanup market conditions resources
            await self._cleanup_market_conditions()
            
            self.logger.info("✅ Market Conditions Agent: Anomaly detection systems shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in market conditions shutdown: {e}")
    
    # ============= BACKGROUND TASKS =============
    
    async def _anomaly_detection_loop(self):
        """Anomaly detection loop."""
        while self.is_running:
            try:
                # Detect anomalies
                await self._detect_anomalies()
                
                await asyncio.sleep(1.0)  # 1 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in anomaly detection loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _regime_analysis_loop(self):
        """Regime analysis loop."""
        while self.is_running:
            try:
                # Analyze market regime
                await self._analyze_market_regime()
                
                await asyncio.sleep(5.0)  # 5 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in regime analysis loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _market_conditions_monitoring_loop(self):
        """Market conditions monitoring loop."""
        while self.is_running:
            try:
                # Monitor market conditions
                await self._monitor_market_conditions()
                
                await asyncio.sleep(2.0)  # 2 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in market conditions monitoring loop: {e}")
                await asyncio.sleep(2.0)
    
    async def _anomaly_reporting_loop(self):
        """Anomaly reporting loop."""
        while self.is_running:
            try:
                # Report anomalies
                await self._report_anomalies()
                
                await asyncio.sleep(10.0)  # 10 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in anomaly reporting loop: {e}")
                await asyncio.sleep(10.0)
    
    async def _detect_anomalies(self):
        """Detect anomalies."""
        try:
            # Placeholder for anomaly detection
            pass
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
    
    async def _analyze_market_regime(self):
        """Analyze market regime."""
        try:
            # Placeholder for market regime analysis
            pass
        except Exception as e:
            self.logger.error(f"Error analyzing market regime: {e}")
    
    async def _monitor_market_conditions(self):
        """Monitor market conditions."""
        try:
            # Placeholder for market conditions monitoring
            pass
        except Exception as e:
            self.logger.error(f"Error monitoring market conditions: {e}")
    
    async def _report_anomalies(self):
        """Report anomalies."""
        try:
            # Placeholder for anomaly reporting
            pass
        except Exception as e:
            self.logger.error(f"Error reporting anomalies: {e}")

    def _get_background_tasks(self) -> List[tuple]:
        """Get background tasks for this agent."""
        return [
            (self._anomaly_detection_loop, "Anomaly Detection", "fast"),
            (self._regime_analysis_loop, "Regime Analysis", "tactical"),
            (self._market_conditions_monitoring_loop, "Market Conditions Monitoring", "tactical"),
            (self._anomaly_reporting_loop, "Anomaly Reporting", "strategic")
        ]
    
    # ============= ANOMALY DETECTION INITIALIZATION =============
    
    async def _initialize_anomaly_detection(self):
        """Initialize anomaly detection components."""
        try:
            # Initialize anomaly detector
            from .core.anomaly_detector import AnomalyDetector
            config = {
                "max_anomalies_per_scan": 5,
                "min_warning_interval": 30,
                "max_warnings_per_evaluation": 3
            }
            self.anomaly_detector = AnomalyDetector(config)
            
            self.logger.info("✅ Anomaly detection components initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing anomaly detection: {e}")
            raise
    
    async def _initialize_early_warning(self):
        """Initialize early warning systems."""
        try:
            # Initialize early warning system
            from .core.early_warning_system import EarlyWarningSystem
            config = {
                "min_warning_interval": 30,
                "max_warnings_per_evaluation": 3
            }
            self.early_warning = EarlyWarningSystem(config)
            
            self.logger.info("✅ Early warning systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing early warning: {e}")
            raise
    
    async def _initialize_regime_analysis(self):
        """Initialize regime analysis."""
        try:
            # Initialize regime analyzer
            from .core.regime_analyzer import RegimeAnalyzer
            self.regime_analyzer = RegimeAnalyzer(self.config)
            
            self.logger.info("✅ Regime analysis initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing regime analysis: {e}")
            raise
    
    # ============= FAST IMBALANCE DETECTION LOOP =============
    
    async def _fast_imbalance_detection_loop(self):
        """Fast market imbalance detection for immediate anomalies (100ms)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Get real-time market data
                market_data = await self._get_real_time_market_data()
                
                if market_data:
                    # Quick imbalance detection (for immediate response)
                    imbalances = await self._detect_immediate_imbalances(market_data)
                    
                    if imbalances:
                        await self._handle_immediate_imbalances(imbalances)
                    
                    # Record operation
                    duration_ms = (time.time() - start_time) * 1000
                    if hasattr(self, 'status_monitor') and self.status_monitor:
                        self.status_monitor.record_operation(duration_ms, len(imbalances) > 0)
                
                await asyncio.sleep(0.1)  # 100ms for fast imbalance detection
                
            except Exception as e:
                self.logger.error(f"Error in fast imbalance detection loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _get_real_time_market_data(self) -> Dict[str, Any]:
        """Get real-time market data from Redis."""
        try:
            # Get latest market data from Redis using async method
            market_data = await self.redis_conn.async_get("market:data:latest")
            
            if market_data:
                return json.loads(market_data)
            else:
                # Fallback to basic market data
                return {
                    "timestamp": time.time(),
                    "symbols": {},
                    "overall_market_state": "unknown"
                }
                
        except Exception as e:
            self.logger.error(f"Error getting real-time market data: {e}")
            return {}
    
    async def _detect_immediate_imbalances(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect immediate market imbalances."""
        try:
            if not self.anomaly_detector:
                return []
            
            # Detect immediate imbalances
            imbalances = await self.anomaly_detector.detect_immediate_imbalances(market_data)
            
            return imbalances
            
        except Exception as e:
            self.logger.error(f"Error detecting immediate imbalances: {e}")
            return []
    
    async def _handle_immediate_imbalances(self, imbalances: List[Dict[str, Any]]):
        """Handle immediate market imbalances."""
        try:
            for imbalance in imbalances:
                imbalance_type = imbalance.get("type", "unknown")
                severity = imbalance.get("severity", "low")
                
                # Log the imbalance
                self.logger.warning(f"Immediate imbalance detected: {imbalance_type} (severity: {severity})")
                
                # Add to detected anomalies
                self.market_state["detected_anomalies"].append({
                    **imbalance,
                    "detection_time": time.time(),
                    "source": "fast_detection"
                })
                
                # Update statistics
                self.stats["anomalies_detected"] += 1
                
                # Publish imbalance alert
                await self._publish_imbalance_alert(imbalance)
                
        except Exception as e:
            self.logger.error(f"Error handling immediate imbalances: {e}")
    
    # ============= TACTICAL ANOMALY SCANNING LOOP =============
    
    async def _tactical_anomaly_scanning_loop(self):
        """Wide anomaly scanning - main work of market conditions agent (1s)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Get comprehensive market data
                market_data = await self._get_comprehensive_market_data()
                
                if market_data:
                    # Perform wide anomaly scan (main functionality)
                    anomalies = await self._scan_for_anomalies(market_data)
                    
                    # Evaluate early warnings based on anomalies
                    warnings = await self._evaluate_warnings(market_data, anomalies)
                    
                    # Process anomalies and warnings
                    await self._process_anomalies_and_warnings(anomalies, warnings)
                    
                    # Update baseline for future detection
                    await self._update_anomaly_baseline(market_data)
                    
                    # Update stats
                    self._update_scanning_stats(anomalies, warnings)
                    
                    # Record operation
                    duration_ms = (time.time() - start_time) * 1000
                    if hasattr(self, 'status_monitor') and self.status_monitor:
                        self.status_monitor.record_operation(duration_ms, True)
                
                await asyncio.sleep(1.0)  # 1s for wide anomaly scanning
                
            except Exception as e:
                self.logger.error(f"Error in tactical anomaly scanning loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _get_comprehensive_market_data(self) -> Dict[str, Any]:
        """Get comprehensive market data."""
        try:
            # Get comprehensive market data from Redis using async method
            market_data = await self.redis_conn.async_get("market:data:comprehensive")
            
            if market_data:
                return json.loads(market_data)
            else:
                # Fallback to basic market data
                return {
                    "timestamp": time.time(),
                    "symbols": {},
                    "market_indicators": {},
                    "overall_market_state": "unknown"
                }
                
        except Exception as e:
            self.logger.error(f"Error getting comprehensive market data: {e}")
            return {}
    
    async def _scan_for_anomalies(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan for market anomalies."""
        try:
            if not self.anomaly_detector:
                return []
            
            # Perform wide anomaly scan
            anomalies = await self.anomaly_detector.scan_for_anomalies(market_data)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error scanning for anomalies: {e}")
            return []
    
    async def _evaluate_warnings(self, market_data: Dict[str, Any], anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate early warnings based on anomalies."""
        try:
            if not self.early_warning:
                return []
            
            # Evaluate warnings
            warnings = await self.early_warning.evaluate_warnings(market_data, anomalies)
            
            return warnings
            
        except Exception as e:
            self.logger.error(f"Error evaluating warnings: {e}")
            return []
    
    async def _process_anomalies_and_warnings(self, anomalies: List[Dict[str, Any]], warnings: List[Dict[str, Any]]):
        """Process detected anomalies and warnings."""
        try:
            # Process anomalies
            for anomaly in anomalies:
                await self._process_anomaly(anomaly)
            
            # Process warnings
            for warning in warnings:
                await self._process_warning(warning)
                
        except Exception as e:
            self.logger.error(f"Error processing anomalies and warnings: {e}")
    
    async def _process_anomaly(self, anomaly: Dict[str, Any]):
        """Process a single anomaly."""
        try:
            anomaly_type = anomaly.get("type", "unknown")
            severity = anomaly.get("severity", "low")
            
            # Add to detected anomalies
            self.market_state["detected_anomalies"].append({
                **anomaly,
                "detection_time": time.time(),
                "source": "tactical_scanning"
            })
            
            # Update statistics
            self.stats["anomalies_detected"] += 1
            
            # Publish anomaly alert
            await self._publish_anomaly_alert(anomaly)
            
        except Exception as e:
            self.logger.error(f"Error processing anomaly: {e}")
    
    async def _process_warning(self, warning: Dict[str, Any]):
        """Process a single warning."""
        try:
            warning_type = warning.get("type", "unknown")
            level = warning.get("level", "low")
            
            # Add to active warnings
            self.market_state["active_warnings"].append({
                **warning,
                "issue_time": time.time(),
                "status": "active"
            })
            
            # Update statistics
            self.stats["warnings_issued"] += 1
            
            # Publish warning alert
            await self._publish_warning_alert(warning)
            
        except Exception as e:
            self.logger.error(f"Error processing warning: {e}")
    
    async def _update_anomaly_baseline(self, market_data: Dict[str, Any]):
        """Update anomaly detection baseline."""
        try:
            if self.anomaly_detector:
                await self.anomaly_detector.update_baseline(market_data)
                
        except Exception as e:
            self.logger.error(f"Error updating anomaly baseline: {e}")
    
    # ============= STRATEGIC REGIME ANALYSIS LOOP =============
    
    async def _strategic_regime_analysis_loop(self):
        """Strategic regime analysis and behavior prediction (60s)."""
        while self.is_running:
            try:
                # Analyze long-term market regime
                await self._analyze_market_regime()
                
                # Update market behavior predictions
                await self._update_behavior_predictions()
                
                # Adjust detection sensitivity based on regime
                await self._adjust_detection_sensitivity()
                
                await asyncio.sleep(60)  # 60s for strategic regime analysis
                
            except Exception as e:
                self.logger.error(f"Error in strategic regime analysis loop: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_market_regime(self):
        """Analyze long-term market regime."""
        try:
            if not self.regime_analyzer:
                return
            
            # Get historical market data
            historical_data = await self._get_historical_market_data()
            
            # Analyze market regime
            regime_analysis = await self.regime_analyzer.analyze_regime(historical_data)
            
            # Update market state
            if regime_analysis:
                new_regime = regime_analysis.get("current_regime", "unknown")
                old_regime = self.market_state["market_regime"]
                
                if new_regime != old_regime:
                    self.market_state["market_regime"] = new_regime
                    self.stats["regime_changes"] += 1
                    
                    # Add to regime history
                    self.market_state["regime_history"].append({
                        "regime": new_regime,
                        "change_time": time.time(),
                        "analysis": regime_analysis
                    })
                    
                    # Publish regime change alert
                    await self._publish_regime_change_alert(new_regime, old_regime)
                
        except Exception as e:
            self.logger.error(f"Error analyzing market regime: {e}")
    
    async def _get_historical_market_data(self) -> Dict[str, Any]:
        """Get historical market data."""
        try:
            # Get historical market data from Redis using async method
            historical_data = await self.redis_conn.async_get("market:data:historical")
            
            if historical_data:
                return json.loads(historical_data)
            else:
                # Fallback to basic historical data
                return {
                    "timestamp": time.time(),
                    "data_points": [],
                    "time_range": "24h"
                }
                
        except Exception as e:
            self.logger.error(f"Error getting historical market data: {e}")
            return {}
    
    async def _update_behavior_predictions(self):
        """Update market behavior predictions."""
        try:
            if not self.regime_analyzer:
                return
            
            # Update behavior predictions based on current regime
            predictions = await self.regime_analyzer.update_predictions(self.market_state["market_regime"])
            
            # Store predictions in market state
            if predictions:
                self.market_state["behavior_predictions"] = predictions
                
        except Exception as e:
            self.logger.error(f"Error updating behavior predictions: {e}")
    
    async def _adjust_detection_sensitivity(self):
        """Adjust detection sensitivity based on regime."""
        try:
            if not self.anomaly_detector:
                return
            
            current_regime = self.market_state["market_regime"]
            
            # Adjust sensitivity based on regime
            if current_regime == "volatile":
                sensitivity = 1.5  # Increase sensitivity
            elif current_regime == "stable":
                sensitivity = 0.7  # Decrease sensitivity
            else:
                sensitivity = 1.0  # Normal sensitivity
            
            self.anomaly_detector.adjust_sensitivity(sensitivity)
            
        except Exception as e:
            self.logger.error(f"Error adjusting detection sensitivity: {e}")
    
    # ============= UTILITY METHODS =============
    
    def _update_scanning_stats(self, anomalies: List[Dict[str, Any]], warnings: List[Dict[str, Any]]):
        """Update scanning statistics."""
        try:
            # Update total scans
            self.stats["total_scans"] += 1
            
            # Update last scan time
            self.market_state["last_scan_time"] = time.time()
            
            # Update anomaly level based on recent anomalies
            if anomalies:
                recent_anomalies = [a for a in self.market_state["detected_anomalies"] 
                                  if time.time() - a.get("detection_time", 0) < 3600]  # Last hour
                
                if recent_anomalies:
                    severity_scores = [self._get_severity_score(a.get("severity", "low")) for a in recent_anomalies]
                    self.market_state["anomaly_level"] = sum(severity_scores) / len(severity_scores)
                else:
                    self.market_state["anomaly_level"] = 0.0
                    
        except Exception as e:
            self.logger.error(f"Error updating scanning stats: {e}")
    
    def _get_severity_score(self, severity: str) -> float:
        """Convert severity string to numeric score."""
        severity_scores = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.9,
            "critical": 1.0
        }
        return severity_scores.get(severity, 0.5)
    
    async def _cleanup_market_conditions(self):
        """Cleanup market conditions components."""
        try:
            # Cleanup anomaly detector
            if self.anomaly_detector:
                await self.anomaly_detector.cleanup()
            
            # Cleanup early warning system
            if self.early_warning:
                await self.early_warning.cleanup()
            
            # Cleanup regime analyzer
            if self.regime_analyzer:
                await self.regime_analyzer.cleanup()
            
            self.logger.info("✅ Market conditions components cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up market conditions: {e}")
    
    # ============= PUBLISHING METHODS =============
    
    async def _publish_imbalance_alert(self, imbalance: Dict[str, Any]):
        """Publish imbalance alert."""
        try:
            imbalance_alert = {
                "alert_type": "market_imbalance",
                "imbalance_data": imbalance,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("market_conditions:imbalance_alerts", json.dumps(imbalance_alert))
            
        except Exception as e:
            self.logger.error(f"Error publishing imbalance alert: {e}")
    
    async def _publish_anomaly_alert(self, anomaly: Dict[str, Any]):
        """Publish anomaly alert."""
        try:
            anomaly_alert = {
                "alert_type": "market_anomaly",
                "anomaly_data": anomaly,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("market_conditions:anomaly_alerts", json.dumps(anomaly_alert))
            
        except Exception as e:
            self.logger.error(f"Error publishing anomaly alert: {e}")
    
    async def _publish_warning_alert(self, warning: Dict[str, Any]):
        """Publish warning alert."""
        try:
            warning_alert = {
                "alert_type": "market_warning",
                "warning_data": warning,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("market_conditions:warning_alerts", json.dumps(warning_alert))
            
        except Exception as e:
            self.logger.error(f"Error publishing warning alert: {e}")
    
    async def _publish_regime_change_alert(self, new_regime: str, old_regime: str):
        """Publish regime change alert."""
        try:
            regime_change_alert = {
                "alert_type": "regime_change",
                "old_regime": old_regime,
                "new_regime": new_regime,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("market_conditions:regime_change_alerts", json.dumps(regime_change_alert))
            
        except Exception as e:
            self.logger.error(f"Error publishing regime change alert: {e}")
    
    # ============= PUBLIC INTERFACE =============
    
    async def get_market_conditions_status(self) -> Dict[str, Any]:
        """Get current market conditions status."""
        return {
            "market_state": self.market_state,
            "stats": self.stats,
            "last_update": time.time()
        }
    
    async def get_detected_anomalies(self) -> List[Dict[str, Any]]:
        """Get currently detected anomalies."""
        return self.market_state.get("detected_anomalies", [])
    
    async def get_active_warnings(self) -> List[Dict[str, Any]]:
        """Get currently active warnings."""
        return self.market_state.get("active_warnings", [])
    
    async def get_market_regime(self) -> Dict[str, Any]:
        """Get current market regime information."""
        return {
            "current_regime": self.market_state["market_regime"],
            "regime_history": self.market_state.get("regime_history", []),
            "behavior_predictions": self.market_state.get("behavior_predictions", {}),
            "last_update": time.time()
        }
    
    async def submit_market_data_for_analysis(self, market_data: Dict[str, Any]) -> bool:
        """Submit market data for analysis."""
        try:
            # Add market data to analysis queue
            analysis_request = {
                "market_data": market_data,
                "timestamp": time.time(),
                "request_type": "analysis"
            }
            
            await self.redis_conn.lpush("market_conditions:analysis_requests", json.dumps(analysis_request))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error submitting market data for analysis: {e}")
            return False
