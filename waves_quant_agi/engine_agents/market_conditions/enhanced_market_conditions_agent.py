#!/usr/bin/env python3
"""
Enhanced Market Conditions Agent - REFACTORED TO USE BASE AGENT
Eliminates duplicate start/stop methods and Redis connection logic.
"""

import asyncio
import time
from typing import Dict, Any, List
from engine_agents.shared_utils import BaseAgent, register_agent

class EnhancedMarketConditionsAgent(BaseAgent):
    """Enhanced market conditions agent using base class."""
    
    def _initialize_agent_components(self):
        """Initialize market conditions specific components."""
        # Initialize market conditions components with mock implementations
        self.anomaly_detector = MockAnomalyDetector()
        self.early_warning = MockEarlyWarning()
        self.regime_analyzer = MockRegimeAnalyzer()
        
        # Initialize market state
        self.current_market_state = {
            "anomaly_level": 0.0,
            "warning_level": "normal",
            "last_scan_time": time.time(),
            "market_regime": "unknown"
        }
        
        # Initialize stats
        self.stats = {
            "total_scans": 0,
            "anomalies_detected": 0,
            "warnings_issued": 0,
            "start_time": time.time()
        }
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Market conditions specific startup logic."""
        # Initialize market conditions components
        self.logger.info("Market conditions components initialized")
    
    async def _agent_specific_shutdown(self):
        """Market conditions specific shutdown logic."""
        # Cleanup market conditions specific resources
        self.logger.info("Market conditions components cleaned up")
    
    # ============= TIER 2: FAST IMBALANCE DETECTION LOOP (100ms) =============
    
    async def _fast_imbalance_detection_loop(self):
        """TIER 2: Fast market imbalance detection for immediate anomalies (100ms)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Get real-time market data using base class method
                market_data = self.get_market_data()
                
                if market_data:
                    # Quick imbalance detection (for immediate response)
                    imbalances = await self._detect_immediate_imbalances(market_data)
                    
                    if imbalances:
                        await self._handle_immediate_imbalances(imbalances)
                    
                    # Record operation for monitoring
                    duration_ms = (time.time() - start_time) * 1000
                    self.status_monitor.record_operation(duration_ms, len(imbalances) == 0)
                
                # TIER 2 timing: 100ms for fast imbalance detection
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in fast imbalance detection loop: {e}")
                await asyncio.sleep(0.1)
    
    # ============= TIER 3: TACTICAL ANOMALY SCANNING LOOP (1s) =============
    
    async def _tactical_anomaly_scanning_loop(self):
        """TIER 3: Wide anomaly scanning - main work of market conditions agent (1s)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Get comprehensive market data
                market_data = self._get_comprehensive_market_data()
                
                if market_data:
                    # Perform wide anomaly scan (main functionality)
                    anomalies = await self.anomaly_detector.scan_for_anomalies(market_data)
                    
                    # Evaluate early warnings based on anomalies
                    warnings = await self.early_warning.evaluate_warnings(market_data, anomalies)
                    
                    # Process anomalies and warnings
                    await self._process_anomalies_and_warnings(anomalies, warnings)
                    
                    # Update baseline for future detection
                    self.anomaly_detector.update_baseline(market_data)
                    
                    # Update stats
                    self._update_scanning_stats(anomalies, warnings)
                    
                    # Record operation for monitoring
                    duration_ms = (time.time() - start_time) * 1000
                    self.status_monitor.record_operation(duration_ms, True)
                
                # TIER 3 timing: 1s for wide anomaly scanning
                await asyncio.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Error in tactical anomaly scanning loop: {e}")
                await asyncio.sleep(1.0)
    
    # ============= TIER 4: STRATEGIC REGIME ANALYSIS LOOP (60s) =============
    
    async def _strategic_regime_analysis_loop(self):
        """TIER 4: Strategic regime analysis and behavior prediction (60s)."""
        while self.is_running:
            try:
                # Analyze long-term market regime
                await self._analyze_market_regime()
                
                # Update market behavior predictions
                await self._update_behavior_predictions()
                
                # Adjust detection sensitivity based on regime
                await self._adjust_detection_sensitivity()
                
                # TIER 4 timing: 60s for strategic regime analysis
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in strategic regime analysis loop: {e}")
                await asyncio.sleep(60)
    
    # ============= TIER 4: HEARTBEAT LOOP (60s) =============
    
    async def _heartbeat_loop(self):
        """TIER 4: Communication heartbeat and status reporting (60s)."""
        while self.is_running:
            try:
                # Send heartbeat to communication hub
                if self.comm_hub:
                    await self._send_heartbeat()
                
                # Update comprehensive stats
                self._update_comprehensive_stats()
                
                # Update agent stats in Redis (same as BaseAgent)
                current_time = time.time()
                agent_stats = {
                    'status': 'running' if self.is_running else 'stopped',
                    'start_time': str(self.start_time) if self.start_time else '0',
                    'uptime_seconds': str(int(current_time - self.start_time)) if self.start_time else '0',
                    'last_heartbeat': str(current_time),
                    'timestamp': str(current_time)
                }
                
                # Update the agent_stats hash using the correct Redis connector method
                if hasattr(self, 'redis_conn') and self.redis_conn:
                    self.redis_conn.hset(f"agent_stats:{self.agent_name}", mapping=agent_stats)
                else:
                    self.logger.warning("Redis connection not available for storing agent status")
                
                # TIER 4 timing: 60s for heartbeat
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(60)
    
    # ============= HELPER METHODS =============
    
    # Market data methods now handled by shared utilities - no duplicate methods
    
    async def _detect_immediate_imbalances(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect immediate market imbalances requiring fast response."""
        imbalances = []
        
        try:
            # Check for rapid price movements
            price_change = market_data.get("price_change", 0)
            if abs(price_change) > 0.02:  # 2% rapid change
                imbalances.append({
                    "type": "rapid_price_movement",
                    "severity": "high",
                    "value": abs(price_change),
                    "details": market_data
                })
            
            # Check for volume spikes
            volume_ratio = market_data.get("volume_ratio", 1.0)
            if volume_ratio > 5.0:  # 5x volume spike
                imbalances.append({
                    "type": "volume_spike",
                    "severity": "medium", 
                    "value": volume_ratio,
                    "details": market_data
                })
                
        except Exception as e:
            self.logger.warning(f"Error detecting immediate imbalances: {e}")
        
        return imbalances
    
    async def _handle_immediate_imbalances(self, imbalances: List[Dict[str, Any]]):
        """Handle immediate imbalances with fast response."""
        for imbalance in imbalances:
            try:
                # Publish immediate alert
                alert_message = {
                    "type": "IMMEDIATE_IMBALANCE_ALERT",
                    "imbalance": imbalance,
                    "timestamp": time.time(),
                    "source": "market_conditions"
                }
                
                self.redis_conn.publish("immediate_alerts", alert_message)
                self.logger.warning(f"IMMEDIATE IMBALANCE: {imbalance['type']}")
                
            except Exception as e:
                self.logger.error(f"Error handling immediate imbalance: {e}")
    
    async def _process_anomalies_and_warnings(self, anomalies: List[Dict[str, Any]], 
                                            warnings: List[Dict[str, Any]]):
        """Process detected anomalies and warnings."""
        
        # Publish anomalies to other agents
        for anomaly in anomalies:
            try:
                anomaly_message = {
                    "type": "MARKET_ANOMALY_ALERT", 
                    "anomaly": anomaly,
                    "timestamp": time.time(),
                    "source": "market_conditions"
                }
                
                if self.comm_hub:
                    await self.comm_hub.publish_message(anomaly_message)
                
            except Exception as e:
                self.logger.error(f"Error publishing anomaly: {e}")
        
        # Publish warnings to other agents
        for warning in warnings:
            try:
                warning_message = {
                    "type": "EARLY_WARNING_ALERT",
                    "warning": warning, 
                    "timestamp": time.time(),
                    "source": "market_conditions"
                }
                
                if self.comm_hub:
                    await self.comm_hub.publish_message(warning_message)
                
            except Exception as e:
                self.logger.error(f"Error publishing warning: {e}")
    
    def _update_scanning_stats(self, anomalies: List[Dict[str, Any]], warnings: List[Dict[str, Any]]):
        """Update scanning statistics."""
        self.stats["total_scans"] += 1
        self.stats["anomalies_detected"] += len(anomalies)
        self.stats["warnings_issued"] += len(warnings)
        
        # Update market state
        self.current_market_state["anomaly_level"] = len(anomalies) / 10.0  # Normalize
        self.current_market_state["warning_level"] = "high" if warnings else "normal"
        self.current_market_state["last_scan_time"] = time.time()
    
    def _update_comprehensive_stats(self):
        """Update comprehensive statistics."""
        # Safe access to components that may not be initialized yet
        detector_stats = {}
        warning_stats = {}
        
        if self.anomaly_detector:
            try:
                detector_stats = self.anomaly_detector.get_detection_stats()
            except Exception as e:
                self.logger.warning(f"Error getting detector stats: {e}")
        
        if self.early_warning:
            try:
                warning_stats = self.early_warning.get_warning_stats()
            except Exception as e:
                self.logger.warning(f"Error getting warning stats: {e}")
        
        self.stats.update({
            "scan_accuracy": detector_stats.get("accuracy", 0.0),
            "detection_rate": detector_stats.get("anomaly_rate", 0.0),
            "warning_rate": warning_stats.get("warnings_issued", 0) / max(self.stats["total_scans"], 1),
            "uptime_hours": (time.time() - self.stats["start_time"]) / 3600
        })
    
    async def _send_heartbeat(self):
        """Send heartbeat to communication hub."""
        try:
            heartbeat_data = {
                "agent": "market_conditions",
                "status": "healthy",
                "stats": self.stats,
                "market_state": self.current_market_state,
                "timestamp": time.time()
            }
            
            if hasattr(self.comm_hub, 'publish_message'):
                await self.comm_hub.publish_message({
                    "type": "AGENT_HEARTBEAT",
                    "data": heartbeat_data
                })
                
        except Exception as e:
            self.logger.warning(f"Error sending heartbeat: {e}")
    
    # Over-engineered placeholder methods removed - complexity eliminated
    
    # ============= MESSAGE HANDLERS =============
    
    async def _handle_market_data(self, message):
        """Handle market data updates."""
        # Market data is handled in the main scanning loops
        pass
    
    async def _handle_strategy_signal(self, message):
        """Handle strategy signals for market impact analysis."""
        # Could analyze market impact of strategy signals
        pass
    
    # ============= PUBLIC INTERFACE =============
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive agent status."""
        # Safe access to components that may not be initialized yet
        detector_stats = {}
        warning_stats = {}
        active_warnings = []
        
        if self.anomaly_detector:
            try:
                detector_stats = self.anomaly_detector.get_detection_stats()
            except Exception as e:
                self.logger.warning(f"Error getting detector stats: {e}")
        
        if self.early_warning:
            try:
                warning_stats = self.early_warning.get_warning_stats()
                active_warnings = self.early_warning.get_active_warnings()
            except Exception as e:
                self.logger.warning(f"Error getting warning stats: {e}")
        
        return {
            "is_running": self.is_running,
            "stats": self.stats,
            "market_state": self.current_market_state,
            "detector_stats": detector_stats,
            "warning_stats": warning_stats,
            "active_warnings": active_warnings,
            "uptime_seconds": int(time.time() - self.stats["start_time"])
        }

# Mock classes for components that don't exist yet
class MockAnomalyDetector:
    async def scan_for_anomalies(self, market_data):
        return []
    
    async def detect_imbalances(self, market_data):
        return []

class MockEarlyWarning:
    async def evaluate_warnings(self, market_data, anomalies):
        return []
    
    async def check_warning_conditions(self, market_data):
        return []

class MockRegimeAnalyzer:
    async def analyze_market_regime(self, market_data):
        return {"regime": "normal", "confidence": 0.8}
