#!/usr/bin/env python3
"""
Enhanced Fees Monitor Agent V3 - ROLE CONSOLIDATED: COST TRACKING ONLY
Removed optimization functionality - now handled by Strategy Engine Agent.
Removed fee optimization functionality - now handled by Strategy Engine Agent.
Focuses exclusively on cost tracking, monitoring, and reporting.
"""

import asyncio
import time
import json
from typing import Dict, Any, List
from engine_agents.shared_utils import BaseAgent, register_agent

class EnhancedFeesMonitorAgentV3(BaseAgent):
    """Enhanced fees monitor agent - focused solely on cost tracking."""
    
    def _initialize_agent_components(self):
        """Initialize fees monitor specific components."""
        # Initialize fees monitoring components
        self.cost_calculator = None
        # self.slippage_tracker = None  # Removed - handled by Execution Agent
        self.cost_analyzer = None
        # self.fee_optimizer = None  # Removed - handled by Strategy Engine Agent
        
        # Cost tracking state
        self.cost_state = {
            "total_fees_paid": 0.0,
            "average_cost_per_trade": 0.0,
            "cost_efficiency_score": 1.0,
            "high_cost_strategies": [],
            "cost_trends": {},
            "last_cost_update": time.time()
        }
        
        # Cost tracking statistics
        self.stats = {
            "total_trades_monitored": 0,
            "total_fees_tracked": 0.0,
            "cost_alerts_triggered": 0,
            # "slippage_events": 0,  # Removed - handled by Execution Agent
            "cost_anomalies_detected": 0,
            "start_time": time.time()
        }
        
        # Register this agent
        register_agent(self.agent_name, self)
    
    async def _agent_specific_startup(self):
        """Fees monitor specific startup logic."""
        try:
            # Initialize cost tracking components
            await self._initialize_cost_components()
            
            # Initialize cost analysis systems (cost tracking only, not optimization)
            await self._initialize_cost_analysis()
            
            self.logger.info("✅ Fees Monitor Agent: Cost tracking systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error in fees monitor startup: {e}")
            raise
    
    async def _agent_specific_shutdown(self):
        """Fees monitor specific shutdown logic."""
        try:
            # Cleanup cost tracking resources
            await self._cleanup_cost_components()
            
            self.logger.info("✅ Fees Monitor Agent: Cost tracking systems shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in fees monitor shutdown: {e}")
    
    # ============= BACKGROUND TASKS =============
    
    async def _profitability_audit_loop(self):
        """Profitability audit loop."""
        while self.is_running:
            try:
                # Audit profitability
                await self._audit_profitability()
                
                await asyncio.sleep(10.0)  # 10 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in profitability audit loop: {e}")
                await asyncio.sleep(10.0)
    
    async def _slippage_tracking_loop(self):
        """Slippage tracking loop."""
        while self.is_running:
            try:
                # Track slippage
                await self._track_slippage()
                
                await asyncio.sleep(1.0)  # 1 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in slippage tracking loop: {e}")
                await asyncio.sleep(1.0)
    
    async def _fee_reporting_loop(self):
        """Fee reporting loop."""
        while self.is_running:
            try:
                # Report fees
                await self._report_fees()
                
                await asyncio.sleep(30.0)  # 30 second cycle
                
            except Exception as e:
                self.logger.error(f"Error in fee reporting loop: {e}")
                await asyncio.sleep(30.0)
    
    async def _audit_profitability(self):
        """Audit profitability."""
        try:
            # Placeholder for profitability audit
            pass
        except Exception as e:
            self.logger.error(f"Error auditing profitability: {e}")
    
    async def _track_slippage(self):
        """Track slippage."""
        try:
            # Placeholder for slippage tracking
            pass
        except Exception as e:
            self.logger.error(f"Error tracking slippage: {e}")
    
    async def _report_fees(self):
        """Report fees."""
        try:
            # Placeholder for fee reporting
            pass
        except Exception as e:
            self.logger.error(f"Error reporting fees: {e}")

    def _get_background_tasks(self) -> List[tuple]:
        """Get background tasks for this agent."""
        return [
            (self._fee_monitoring_loop, "Fee Monitoring", "fast"),
            (self._profitability_audit_loop, "Profitability Audit", "tactical"),
            (self._slippage_tracking_loop, "Slippage Tracking", "fast"),
            (self._fee_reporting_loop, "Fee Reporting", "strategic")
        ]
    
    # ============= COST COMPONENT INITIALIZATION =============
    
    async def _initialize_cost_components(self):
        """Initialize cost tracking components."""
        try:
            # Initialize cost calculator
            from .core.cost_calculator import CostCalculator
            self.cost_calculator = CostCalculator(self.config)
            
            # Initialize slippage tracker (removed - handled by Execution Agent)
            # from .core.slippage_tracker import SlippageTracker
            # self.slippage_tracker = SlippageTracker(self.config)
            
            # Initialize cost analyzer
            from .core.cost_analyzer import CostAnalyzer
            self.cost_analyzer = CostAnalyzer(self.config)
            
            self.logger.info("✅ Cost tracking components initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing cost components: {e}")
            raise
    
    async def _initialize_cost_analysis(self):
        """Initialize cost analysis systems."""
        try:
            # Set up cost analysis models (cost tracking only, not optimization)
            await self.cost_analyzer.initialize_analysis()
            
            # Set up cost tracking thresholds (cost monitoring only, not optimization)
            await self._setup_cost_thresholds()
            
            self.logger.info("✅ Cost analysis systems initialized")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing cost analysis: {e}")
            raise
    
    async def _setup_cost_thresholds(self):
        """Set up cost tracking thresholds."""
        try:
            # Set up default cost thresholds
            cost_thresholds = {
                "high_cost_alert": 0.001,  # 0.1% of trade value
                "excessive_cost_alert": 0.005,  # 0.5% of trade value
                # "slippage_alert": 0.0005,  # 0.05% slippage  # Removed - handled by Execution Agent
                "cost_efficiency_threshold": 0.8  # 80% efficiency
            }
            
            # Store thresholds in Redis for other agents to access
            await self.redis_conn.hset("cost:thresholds", mapping=cost_thresholds)
            
        except Exception as e:
            self.logger.error(f"❌ Error setting up cost thresholds: {e}")
    
    # ============= COST TRACKING LOOP =============
    
    async def _cost_tracking_loop(self):
        """Main cost tracking loop (100ms intervals)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Track real-time costs
                costs_tracked = await self._track_real_time_costs()
                
                # Update cost state
                if costs_tracked > 0:
                    self._update_cost_state()
                
                # Record operation
                duration_ms = (time.time() - start_time) * 1000
                if hasattr(self, 'status_monitor') and self.status_monitor:
                    self.status_monitor.record_operation(duration_ms, costs_tracked > 0)
                
                await asyncio.sleep(0.1)  # 100ms cost tracking cycle
                
            except Exception as e:
                self.logger.error(f"Error in cost tracking loop: {e}")
                await asyncio.sleep(0.1)
    
    async def _track_real_time_costs(self) -> int:
        """Track real-time costs and return number of costs tracked."""
        try:
            costs_tracked = 0
            
            # Get pending cost tracking requests
            cost_requests = await self._get_pending_cost_requests()
            
            for request in cost_requests:
                if await self._process_cost_request(request):
                    costs_tracked += 1
            
            return costs_tracked
            
        except Exception as e:
            self.logger.error(f"Error tracking real-time costs: {e}")
            return 0
    
    async def _get_pending_cost_requests(self) -> List[Dict[str, Any]]:
        """Get pending cost tracking requests from Redis."""
        try:
            # Get cost tracking requests from Redis queue
            cost_requests = await self.redis_conn.lrange("cost:tracking_requests", 0, 9)
            
            requests = []
            for request in cost_requests:
                try:
                    requests.append(json.loads(request))
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid cost request format: {request}")
            
            return requests
            
        except Exception as e:
            self.logger.error(f"Error getting pending cost requests: {e}")
            return []
    
    async def _process_cost_request(self, request: Dict[str, Any]) -> bool:
        """Process a single cost tracking request."""
        try:
            request_type = request.get("type", "unknown")
            request_data = request.get("data", {})
            
            if request_type == "trade_cost":
                return await self._track_trade_cost(request_data)
            elif request_type == "order_cost":
                return await self._track_order_cost(request_data)
            elif request_type == "strategy_cost":
                return await self._track_strategy_cost(request_data)
            else:
                self.logger.warning(f"Unknown cost request type: {request_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing cost request: {e}")
            return False
    
    async def _track_trade_cost(self, trade_data: Dict[str, Any]) -> bool:
        """Track costs for a completed trade."""
        try:
            if not self.cost_calculator:
                return False
            
            # Calculate trade costs
            trade_costs = await self.cost_calculator.calculate_trade_costs(trade_data)
            
            # Update statistics
            self.stats["total_trades_monitored"] += 1
            self.stats["total_fees_tracked"] += trade_costs.get("total_fees", 0.0)
            
            # Update cost state
            self._update_trade_cost_metrics(trade_costs)
            
            # Check for cost alerts
            await self._check_cost_alerts(trade_costs)
            
            # Publish cost update
            await self._publish_cost_update("trade_cost", trade_costs)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error tracking trade cost: {e}")
            return False
    
    async def _track_order_cost(self, order_data: Dict[str, Any]) -> bool:
        """Track costs for an order update."""
        try:
            if not self.cost_calculator:
                return False
            
            # Track order costs
            order_costs = await self.cost_calculator.track_order_costs(order_data)
            
            # Update cost state
            self._update_order_cost_metrics(order_costs)
            
            # Publish cost update
            await self._publish_cost_update("order_cost", order_costs)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error tracking order cost: {e}")
            return False
    
    async def _track_strategy_cost(self, strategy_data: Dict[str, Any]) -> bool:
        """Track costs for a strategy."""
        try:
            if not self.cost_calculator:
                return False
            
            # Calculate strategy costs
            strategy_costs = await self.cost_calculator.calculate_strategy_costs(strategy_data)
            
            # Update cost state
            self._update_strategy_cost_metrics(strategy_costs)
            
            # Check for strategy cost alerts
            await self._check_strategy_cost_alerts(strategy_costs)
            
            # Publish cost update
            await self._publish_cost_update("strategy_cost", strategy_costs)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error tracking strategy cost: {e}")
            return False
    
    # ============= COST ANALYSIS LOOP =============
    
    async def _cost_analysis_loop(self):
        """Cost analysis loop (30s intervals)."""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Perform cost analysis
                analysis_results = await self._perform_cost_analysis()
                
                # Update cost trends
                if analysis_results:
                    self._update_cost_trends(analysis_results)
                
                # Publish cost analysis
                await self._publish_cost_analysis(analysis_results)
                
                # Record operation
                duration_ms = (time.time() - start_time) * 1000
                if hasattr(self, 'status_monitor') and self.status_monitor:
                    self.status_monitor.record_operation(duration_ms, True)
                
                await asyncio.sleep(30)  # 30s cost analysis cycle
                
            except Exception as e:
                self.logger.error(f"Error in cost analysis loop: {e}")
                await asyncio.sleep(30)
    
    async def _perform_cost_analysis(self) -> Dict[str, Any]:
        """Perform comprehensive cost analysis."""
        try:
            if not self.cost_analyzer:
                return {}
            
            # Get current cost data
            current_costs = {
                "total_fees": self.stats["total_fees_tracked"],
                "trade_count": self.stats["total_trades_monitored"],
                "cost_state": self.cost_state
            }
            
            # Perform analysis
            analysis_results = await self.cost_analyzer.analyze_costs(current_costs)
            
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error performing cost analysis: {e}")
            return {}
    
    # ============= SLIPPAGE MONITORING LOOP =============
    # REMOVED - Handled by Execution Agent
    
    # async def _slippage_monitoring_loop(self):
    #     """Slippage monitoring loop (100ms intervals) - REMOVED."""
    #     pass
    
    # async def _monitor_slippage_events(self) -> int:
    #     """Monitor for slippage events - REMOVED."""
    #     pass
    
    # async def _process_slippage_event(self, slippage_event: Dict[str, Any]):
    #     """Process slippage event - REMOVED."""
    #     pass
    
    # ============= COST ALERT METHODS =============
    
    async def _check_cost_alerts(self, trade_costs: Dict[str, Any]):
        """Check for cost alerts."""
        try:
            total_fees = trade_costs.get("total_fees", 0.0)
            trade_value = trade_costs.get("trade_value", 1.0)
            
            if trade_value > 0:
                cost_percentage = total_fees / trade_value
                
                # Check high cost alert
                if cost_percentage > 0.001:  # 0.1%
                    await self._trigger_cost_alert("high_cost", trade_costs)
                
                # Check excessive cost alert
                if cost_percentage > 0.005:  # 0.5%
                    await self._trigger_cost_alert("excessive_cost", trade_costs)
                    
        except Exception as e:
            self.logger.error(f"Error checking cost alerts: {e}")
    
    async def _check_strategy_cost_alerts(self, strategy_costs: Dict[str, Any]):
        """Check for strategy cost alerts."""
        try:
            efficiency_score = strategy_costs.get("efficiency_score", 1.0)
            
            # Check cost efficiency threshold
            if efficiency_score < 0.8:  # 80% efficiency
                await self._trigger_cost_alert("low_efficiency", strategy_costs)
                
        except Exception as e:
            self.logger.error(f"Error checking strategy cost alerts: {e}")
    
    async def _trigger_cost_alert(self, alert_type: str, cost_data: Dict[str, Any]):
        """Trigger a cost alert."""
        try:
            alert_data = {
                "alert_type": alert_type,
                "cost_data": cost_data,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            # Update statistics
            self.stats["cost_alerts_triggered"] += 1
            
            # Publish cost alert
            await self.redis_conn.publish_async("cost:alerts", json.dumps(alert_data))
            
            self.logger.warning(f"Cost alert triggered: {alert_type}")
            
        except Exception as e:
            self.logger.error(f"Error triggering cost alert: {e}")
    
    # async def _trigger_slippage_alert(self, slippage_event: Dict[str, Any]):
    #     """Trigger slippage alert - REMOVED (handled by Execution Agent)."""
    #     pass
    
    # ============= UTILITY METHODS =============
    
    def _update_cost_state(self):
        """Update cost state with current information."""
        try:
            # Update last cost update timestamp
            self.cost_state["last_cost_update"] = time.time()
            
            # Calculate average cost per trade
            if self.stats["total_trades_monitored"] > 0:
                self.cost_state["average_cost_per_trade"] = (
                    self.stats["total_fees_tracked"] / self.stats["total_trades_monitored"]
                )
                
        except Exception as e:
            self.logger.error(f"Error updating cost state: {e}")
    
    def _update_trade_cost_metrics(self, trade_costs: Dict[str, Any]):
        """Update trade cost metrics."""
        try:
            # Update total fees paid
            self.cost_state["total_fees_paid"] += trade_costs.get("total_fees", 0.0)
            
            # Update cost efficiency score
            efficiency = trade_costs.get("efficiency_score", 1.0)
            self.cost_state["cost_efficiency_score"] = (
                (self.cost_state["cost_efficiency_score"] + efficiency) / 2
            )
            
        except Exception as e:
            self.logger.error(f"Error updating trade cost metrics: {e}")
    
    def _update_order_cost_metrics(self, order_costs: Dict[str, Any]):
        """Update order cost metrics."""
        try:
            # Update order-specific cost metrics
            # This can be expanded based on specific requirements
            pass  # Placeholder for future implementation
            
        except Exception as e:
            self.logger.error(f"Error updating order cost metrics: {e}")
    
    def _update_strategy_cost_metrics(self, strategy_costs: Dict[str, Any]):
        """Update strategy cost metrics."""
        try:
            # Update strategy-specific cost metrics
            high_cost_strategies = strategy_costs.get("high_cost_strategies", [])
            
            for strategy in high_cost_strategies:
                if strategy not in self.cost_state["high_cost_strategies"]:
                    self.cost_state["high_cost_strategies"].append(strategy)
            
        except Exception as e:
            self.logger.error(f"Error updating strategy cost metrics: {e}")
    
    def _update_cost_trends(self, analysis_results: Dict[str, Any]):
        """Update cost trends from analysis results."""
        try:
            # Update cost trends based on analysis
            trends = analysis_results.get("trends", {})
            
            for trend_type, trend_data in trends.items():
                self.cost_state["cost_trends"][trend_type] = {
                    "data": trend_data,
                    "last_update": time.time()
                }
                
        except Exception as e:
            self.logger.error(f"Error updating cost trends: {e}")
    
    async def _cleanup_cost_components(self):
        """Cleanup cost tracking components."""
        try:
            # Cleanup cost calculator
            if self.cost_calculator:
                await self.cost_calculator.cleanup()
            
            # Cleanup slippage tracker (removed - handled by Execution Agent)
            # if self.slippage_tracker:
            #     await self.slippage_tracker.cleanup()
            
            # Cleanup cost analyzer
            if self.cost_analyzer:
                await self.cost_analyzer.cleanup()
            
            self.logger.info("✅ Cost tracking components cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Error cleaning up cost components: {e}")
    
    # ============= PUBLISHING METHODS =============
    
    async def _publish_cost_update(self, update_type: str, cost_data: Dict[str, Any]):
        """Publish cost update."""
        try:
            cost_update = {
                "update_type": update_type,
                "cost_data": cost_data,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("cost:updates", json.dumps(cost_update))
            
        except Exception as e:
            self.logger.error(f"Error publishing cost update: {e}")
    
    async def _publish_cost_analysis(self, analysis_results: Dict[str, Any]):
        """Publish cost analysis."""
        try:
            analysis_report = {
                "analysis_results": analysis_results,
                "timestamp": time.time(),
                "agent": self.agent_name
            }
            
            await self.redis_conn.publish_async("cost:analysis_reports", json.dumps(analysis_report))
            
        except Exception as e:
            self.logger.error(f"Error publishing cost analysis: {e}")
    
    # async def _publish_slippage_update(self, slippage_event: Dict[str, Any]):
    #     """Publish slippage update - REMOVED (handled by Execution Agent)."""
    #     pass
    
    # ============= PUBLIC INTERFACE =============
    
    async def get_cost_status(self) -> Dict[str, Any]:
        """Get current cost tracking status."""
        return {
            "cost_state": self.cost_state,
            "stats": self.stats,
            "last_update": time.time()
        }
    
    async def get_cost_metrics(self) -> Dict[str, Any]:
        """Get current cost metrics."""
        return {
            "total_fees": self.stats["total_fees_tracked"],
            "average_cost_per_trade": self.cost_state["average_cost_per_trade"],
            "cost_efficiency_score": self.cost_state["cost_efficiency_score"],
            "high_cost_strategies": self.cost_state["high_cost_strategies"],
            "last_update": time.time()
        }
    
    async def submit_cost_tracking_request(self, request_type: str, data: Dict[str, Any]) -> bool:
        """Submit a cost tracking request."""
        try:
            cost_request = {
                "type": request_type,
                "data": data,
                "timestamp": time.time()
            }
            
            # Add to cost tracking queue
            await self.redis_conn.lpush("cost:tracking_requests", json.dumps(cost_request))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error submitting cost tracking request: {e}")
            return False
