#!/usr/bin/env python3
"""
Enhanced Intelligence Agent - ROLE CONSOLIDATED: PATTERN RECOGNITION ONLY
Removed learning functionality - now handled by Strategy Engine Agent.
Focuses exclusively on pattern recognition, signal generation, and market intelligence.
"""

import asyncio
import time
import json
from typing import Dict, Any, List
from engine_agents.shared_utils import BaseAgent, register_agent

class EnhancedIntelligenceAgent(BaseAgent):
    """Enhanced intelligence agent - focused solely on pattern recognition."""
    
    def _initialize_agent_components(self):
        """Initialize intelligence specific components."""
        # Initialize intelligence components
        self.pattern_recognizer = None
        self.signal_generator = None
        self.market_intelligence = None
        
        # Pattern recognition state
        self.intelligence_state = {
            "detected_patterns": [],
            "active_signals": [],
            "pattern_confidence": {},
            "last_pattern_scan": time.time(),
            "pattern_history": []
        }
        
        # Pattern recognition statistics
        self.stats = {
            "total_pattern_scans": 0,
            "patterns_detected": 0,
            "signals_generated": 0,
            "high_confidence_patterns": 0,
            "false_positives": 0,
            "start_time": time.time()
        }
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Intelligence specific startup logic."""
        try:
            # Initialize pattern recognition components
            await self._initialize_pattern_recognition()
            
            # Initialize pattern analysis systems
            await self._initialize_pattern_analysis()
            
            # Initialize market intelligence
            await self._initialize_market_intelligence()
            
            self.logger.info("✅ Intelligence Agent: Pattern recognition systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error in intelligence startup: {e}")
            raise
    
    async def _agent_specific_shutdown(self):
        """Intelligence specific shutdown logic."""
        try:
            # Cleanup intelligence resources
            await self._cleanup_intelligence_components()
            
            self.logger.info("✅ Intelligence Agent: Pattern recognition systems shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in intelligence shutdown: {e}")
    
    # ============= BACKGROUND TASKS =============
    
    async def _intelligence_gathering_loop(self):
        """Intelligence gathering loop."""
        while self.is_running:
            try:
                # Gather intelligence
                await self._gather_intelligence()
                
                await asyncio.sleep(5.0)  # 5 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in intelligence gathering loop: {e}")
                await asyncio.sleep(5.0)
    
    async def _intelligence_reporting_loop(self):
        """Intelligence reporting loop."""
        while self.is_running:
            try:
                # Report intelligence
                await self._report_intelligence()
                
                await asyncio.sleep(30.0)  # 30 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in intelligence reporting loop: {e}")
                await asyncio.sleep(30.0)
    
    async def _gather_intelligence(self):
        """Gather intelligence."""
        try:
            # Placeholder for intelligence gathering
            pass
        except Exception as e:
            self.logger.error(f"Error gathering intelligence: {e}")
    
    async def _report_intelligence(self):
        """Report intelligence."""
        try:
            # Placeholder for intelligence reporting
            pass
        except Exception as e:
            self.logger.error(f"Error reporting intelligence: {e}")

    def _get_background_tasks(self) -> List[tuple]:
        """Get background tasks for this agent."""
        return [
            (self._pattern_recognition_loop, "Pattern Recognition", "fast"),
            (self._intelligence_gathering_loop, "Intelligence Gathering", "tactical"),
            (self._pattern_analysis_loop, "Pattern Analysis", "fast"),
            (self._intelligence_reporting_loop, "Intelligence Reporting", "strategic")
        ]
    
    # ============= PATTERN RECOGNITION INITIALIZATION =============
    
    async def _initialize_pattern_recognition(self):
        """Initialize pattern recognition components."""
        try:
            # Initialize pattern recognizer
            from .core.pattern_recognizer import PatternRecognizer
            self.logger.info("Importing PatternRecognizer...")
            
            self.pattern_recognizer = PatternRecognizer(self.config)
            self.logger.info("PatternRecognizer instance created")
            
            self.logger.info("✅ Pattern recognition components initialized")
            
        except ImportError as e:
            self.logger.error(f"❌ Import error in pattern recognition: {e}")
            self.pattern_recognizer = None
        except Exception as e:
            self.logger.error(f"❌ Error initializing pattern recognition: {e}")
            self.pattern_recognizer = None
    
    async def _initialize_pattern_analysis(self):
        """Initialize pattern analysis systems."""
        try:
            # Initialize pattern analyzer
            from .core.pattern_analyzer import PatternAnalyzer
            self.logger.info("Importing PatternAnalyzer...")
            
            self.pattern_analyzer = PatternAnalyzer(self.config)
            self.logger.info("PatternAnalyzer instance created")
            
            self.logger.info("✅ Pattern analysis systems initialized")
            
        except ImportError as e:
            self.logger.error(f"❌ Import error in pattern analysis: {e}")
            self.pattern_analyzer = None
        except Exception as e:
            self.logger.error(f"❌ Error initializing pattern analysis: {e}")
            self.pattern_analyzer = None
    
    async def _initialize_market_intelligence(self):
        """Initialize market intelligence."""
        try:
            # Initialize market intelligence
            from .core.market_intelligence import MarketIntelligence
            self.logger.info("Importing MarketIntelligence...")
            
            self.market_intelligence = MarketIntelligence(self.config)
            self.logger.info("MarketIntelligence instance created")
            
            self.logger.info("✅ Market intelligence initialized")
            
        except ImportError as e:
            self.logger.error(f"❌ Import error in market intelligence: {e}")
            self.market_intelligence = None
        except Exception as e:
            self.logger.error(f"❌ Error initializing market intelligence: {e}")
            self.market_intelligence = None
    
    # ============= PATTERN RECOGNITION LOOP =============
    
    async def _pattern_recognition_loop(self):
        """Main pattern recognition loop (1s intervals)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Get market data for pattern recognition
                market_data = await self._get_market_data_for_patterns()
                
                if market_data:
                    # Perform pattern recognition
                    patterns = await self._recognize_patterns(market_data)
                    
                    if patterns:
                        await self._process_patterns(patterns)
                    
                    # Update statistics
                    self.stats["total_pattern_scans"] += 1
                    self.stats["patterns_detected"] += len(patterns)
                    
                    # Record operation
                    duration_ms = (time.time() - start_time) * 1000
                    if hasattr(self, 'status_monitor') and self.status_monitor:
                        self.status_monitor.record_operation(duration_ms, len(patterns) > 0)
                
                await asyncio.sleep(1.0)  # 1s for pattern recognition
                
            except Exception as e:
                self.logger.error(f"Error in pattern recognition loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _get_market_data_for_patterns(self) -> Dict[str, Any]:
        """Get market data for pattern recognition."""
        try:
            # Get market data from Redis
            market_data = await self.redis_conn.get("market:data:patterns")
            
            if market_data:
                return json.loads(market_data)
            else:
                # Fallback to basic market data
                return {
                    "timestamp": time.time(),
                    "price_data": {},
                    "volume_data": {},
                    "indicator_data": {}
                }
                
        except Exception as e:
            self.logger.error(f"Error getting market data for patterns: {e}")
            return {}
    
    async def _recognize_patterns(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recognize patterns in market data."""
        try:
            if not self.pattern_recognizer:
                self.logger.warning("Pattern recognizer not initialized, skipping pattern recognition")
                return []
            
            # Perform pattern recognition
            patterns = await self.pattern_recognizer.recognize_patterns(market_data)
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error recognizing patterns: {e}")
            return []
    
    async def _process_patterns(self, patterns: List[Dict[str, Any]]):
        """Process detected patterns."""
        try:
            for pattern in patterns:
                pattern_type = pattern.get("type", "unknown")
                confidence = pattern.get("confidence", 0.0)
                
                # Add to detected patterns
                self.intelligence_state["detected_patterns"].append({
                    **pattern,
                    "detection_time": time.time(),
                    "status": "active"
                })
                
                # Update pattern confidence
                self.intelligence_state["pattern_confidence"][pattern_type] = confidence
                
                # Track high confidence patterns
                if confidence > 0.8:
                    self.stats["high_confidence_patterns"] += 1
                
                # Publish pattern alert
                await self._publish_pattern_alert(pattern)
                
        except Exception as e:
            self.logger.error(f"Error processing patterns: {e}")
    
    # ============= PATTERN ANALYSIS LOOP =============
    
    async def _pattern_analysis_loop(self):
        """Pattern analysis loop (100ms intervals)."""
        while self.is_running:
            try:
                # Analyze patterns for insights
                patterns_analyzed = await self._analyze_patterns_for_insights()
                
                # Update pattern statistics
                if patterns_analyzed > 0:
                    self.stats["patterns_analyzed"] += patterns_analyzed
                
                await asyncio.sleep(0.1)  # 100ms for pattern analysis
                
            except Exception as e:
                self.logger.error(f"Error in pattern analysis loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _analyze_patterns_for_insights(self) -> int:
        """Analyze patterns for market insights (not signals)."""
        try:
            patterns_analyzed = 0
            
            # Get active patterns
            active_patterns = [p for p in self.intelligence_state["detected_patterns"] 
                             if p.get("status") == "active"]
            
            for pattern in active_patterns:
                # Analyze pattern for market insights
                insights = await self._extract_pattern_insights(pattern)
                
                if insights:
                    # Store insights for strategy engine consumption
                    await self._store_pattern_insights(pattern, insights)
                    patterns_analyzed += 1
            
            return patterns_analyzed
            
        except Exception as e:
            self.logger.error(f"Error analyzing patterns for insights: {e}")
            return 0
    
    # ============= MARKET INTELLIGENCE LOOP =============
    
    async def _market_intelligence_loop(self):
        """Market intelligence loop (30s intervals)."""
        while self.is_running:
            try:
                # Update market intelligence
                intelligence_update = await self._update_market_intelligence()
                
                # Process intelligence insights
                if intelligence_update:
                    await self._process_intelligence_insights(intelligence_update)
                
                await asyncio.sleep(30)  # 30s for market intelligence
                
            except Exception as e:
                self.logger.error(f"Error in market intelligence loop: {e}")
                await asyncio.sleep(30)
    
    async def _update_market_intelligence(self) -> Dict[str, Any]:
        """Update market intelligence."""
        try:
            if not self.market_intelligence:
                return {}
            
            # Update market intelligence
            intelligence_update = await self.market_intelligence.update_intelligence()
            
            return intelligence_update
            
        except Exception as e:
            self.logger.error(f"Error updating market intelligence: {e}")
            return {}
    
    async def _process_intelligence_insights(self, intelligence_update: Dict[str, Any]):
        """Process intelligence insights."""
        try:
            insights = intelligence_update.get("insights", [])
            
            for insight in insights:
                insight_type = insight.get("type", "unknown")
                
                # Process insight based on type
                if insight_type == "market_regime":
                    await self._process_market_regime_insight(insight)
                elif insight_type == "correlation":
                    await self._process_correlation_insight(insight)
                elif insight_type == "volatility":
                    await self._process_volatility_insight(insight)
                
                # Publish intelligence insight
                await self._publish_intelligence_insight(insight)
                
        except Exception as e:
            self.logger.error(f"Error processing intelligence insights: {e}")
    
    async def _process_market_regime_insight(self, insight: Dict[str, Any]):
        """Process market regime insight."""
        try:
            regime = insight.get("regime", "unknown")
            confidence = insight.get("confidence", 0.0)
            
            # Update pattern recognition sensitivity based on regime
            if self.pattern_recognizer:
                await self.pattern_recognizer.adjust_sensitivity_for_regime(regime, confidence)
                
        except Exception as e:
            self.logger.error(f"Error processing market regime insight: {e}")
    
    async def _process_correlation_insight(self, insight: Dict[str, Any]):
        """Process correlation insight."""
        try:
            correlation_data = insight.get("correlation_data", {})
            
            # Update pattern recognition with correlation data
            if self.pattern_recognizer:
                await self.pattern_recognizer.update_correlation_data(correlation_data)
                
        except Exception as e:
            self.logger.error(f"Error processing correlation insight: {e}")
    
    async def _process_volatility_insight(self, insight: Dict[str, Any]):
        """Process volatility insight."""
        try:
            volatility_level = insight.get("volatility_level", "normal")
            
            # Update signal generation based on volatility
            if self.signal_generator:
                await self.signal_generator.adjust_for_volatility(volatility_level)
                
        except Exception as e:
            self.logger.error(f"Error processing volatility insight: {e}")
    
    # ============= UTILITY METHODS =============
    
    async def _cleanup_intelligence_components(self):
        """Cleanup intelligence components."""
        try:
            # Cleanup pattern recognizer
            if self.pattern_recognizer:
                await self.pattern_recognizer.cleanup()
            
            # Cleanup signal generator
            if self.signal_generator:
                await self.signal_generator.cleanup()
            
            # Cleanup market intelligence
            if self.market_intelligence:
                await self.market_intelligence.cleanup()
            
            self.logger.info("✅ Intelligence components cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up intelligence components: {e}")
    
    # ============= PUBLISHING METHODS =============
    
    async def _publish_pattern_alert(self, pattern: Dict[str, Any]):
        """Publish pattern alert."""
        try:
            pattern_alert = {
                "alert_type": "pattern_detected",
                "pattern_data": pattern,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("intelligence:pattern_alerts", json.dumps(pattern_alert))
            
        except Exception as e:
            self.logger.error(f"Error publishing pattern alert: {e}")
    
    async def _publish_signal_alert(self, signal: Dict[str, Any]):
        """Publish signal alert."""
        try:
            signal_alert = {
                "alert_type": "signal_generated",
                "signal_data": signal,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("intelligence:signal_alerts", json.dumps(signal_alert))
            
        except Exception as e:
            self.logger.error(f"Error publishing signal alert: {e}")
    
    async def _publish_intelligence_insight(self, insight: Dict[str, Any]):
        """Publish intelligence insight."""
        try:
            intelligence_alert = {
                "alert_type": "intelligence_insight",
                "insight_data": insight,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("intelligence:insight_alerts", json.dumps(intelligence_alert))
            
        except Exception as e:
            self.logger.error(f"Error publishing intelligence insight: {e}")
    
    # ============= PUBLIC INTERFACE =============
    
    async def get_intelligence_status(self) -> Dict[str, Any]:
        """Get current intelligence status."""
        return {
            "intelligence_state": self.intelligence_state,
            "stats": self.stats,
            "last_update": time.time()
        }
    
    async def get_detected_patterns(self) -> List[Dict[str, Any]]:
        """Get currently detected patterns."""
        return self.intelligence_state.get("detected_patterns", [])
    
    async def get_active_signals(self) -> List[Dict[str, Any]]:
        """Get currently active signals."""
        return self.intelligence_state.get("active_signals", [])
    
    async def get_pattern_confidence(self) -> Dict[str, Any]:
        """Get pattern confidence levels."""
        return self.intelligence_state.get("pattern_confidence", {})
    
    async def submit_market_data_for_pattern_recognition(self, market_data: Dict[str, Any]) -> bool:
        """Submit market data for pattern recognition."""
        try:
            # Add market data to pattern recognition queue
            recognition_request = {
                "market_data": market_data,
                "timestamp": time.time(),
                "request_type": "pattern_recognition"
            }
            
            await self.redis_conn.lpush("intelligence:pattern_requests", json.dumps(recognition_request))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error submitting market data for pattern recognition: {e}")
            return False
