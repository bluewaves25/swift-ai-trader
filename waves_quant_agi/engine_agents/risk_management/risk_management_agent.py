#!/usr/bin/env python3
"""
Risk Management Agent
Orchestrates comprehensive risk management with quantum-inspired analysis.
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
import redis
import pandas as pd
from .logs.risk_management_logger import RiskManagementLogger
from .risk_management_core import RiskManagementCore

class RiskManagementAgent:
    """Main orchestrator for comprehensive risk management with quantum-inspired analysis."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        
        # Initialize Redis connection
        self.redis_client = self._init_redis()
        self.logger = RiskManagementLogger("risk_management_agent", self.redis_client)
        
        # Initialize risk management components
        self._init_risk_components()
        
        # Performance tracking
        self.stats = {
            "total_evaluations": 0,
            "approved_decisions": 0,
            "denied_decisions": 0,
            "risk_alerts": 0,
            "threshold_breaches": 0,
            "portfolio_analyses": 0,
            "start_time": time.time(),
            "last_evaluation_time": 0
        }

    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            return redis.Redis(
                host=self.config.get("redis_host", "localhost"),
                port=self.config.get("redis_port", 6379),
                db=self.config.get("redis_db", 0),
                decode_responses=True
            )
        except Exception as e:
            self.logger.log_error(f"Failed to initialize Redis: {e}")
            return None

    def _init_risk_components(self):
        """Initialize risk management components."""
        try:
            # Initialize risk management core
            self.risk_core = RiskManagementCore(self.config)
            
            self.logger.log("Risk management components initialized successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error initializing risk components: {e}")

    async def start(self):
        """Start the risk management agent."""
        try:
            self.logger.log("Starting Risk Management Agent...")
            self.is_running = True
            
            # Start all risk management tasks
            tasks = [
                asyncio.create_task(self._risk_evaluation_loop()),
                asyncio.create_task(self._portfolio_monitoring_loop()),
                asyncio.create_task(self._risk_alert_loop()),
                asyncio.create_task(self._threshold_monitoring_loop()),
                asyncio.create_task(self._capital_allocation_loop()),
                asyncio.create_task(self._stats_reporting_loop())
            ]
            
            # Start all tasks
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logger.log_error(f"Error starting risk management agent: {e}")
            await self.stop()

    async def stop(self):
        """Stop the risk management agent gracefully."""
        self.logger.log("Stopping Risk Management Agent...")
        self.is_running = False
        
        try:
            self.logger.log("Risk Management Agent stopped successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error stopping risk management agent: {e}")

    async def _risk_evaluation_loop(self):
        """Periodic risk evaluation loop."""
        while self.is_running:
            try:
                # Get strategy data from Redis
                strategy_data = await self._get_strategy_data()
                
                if not strategy_data.empty:
                    # Perform risk evaluation
                    risk_decisions = await self.risk_core.evaluate_risk(strategy_data)
                    
                    if risk_decisions:
                        self.stats["total_evaluations"] += len(risk_decisions)
                        self.stats["last_evaluation_time"] = time.time()
                        
                        # Count decisions
                        approved = sum(1 for d in risk_decisions if d.get("status") == "approve")
                        denied = len(risk_decisions) - approved
                        
                        self.stats["approved_decisions"] += approved
                        self.stats["denied_decisions"] += denied
                        
                        self.logger.log_risk_assessment("strategy_evaluation", {
                            "decision_count": len(risk_decisions),
                            "approved_count": approved,
                            "denied_count": denied,
                            "description": f"Evaluated {len(risk_decisions)} strategies"
                        })
                
                await asyncio.sleep(self.config.get("risk_evaluation_interval", 60))
                
            except Exception as e:
                self.logger.log_error(f"Error in risk evaluation loop: {e}")
                await asyncio.sleep(30)

    async def _portfolio_monitoring_loop(self):
        """Periodic portfolio monitoring loop."""
        while self.is_running:
            try:
                # Get portfolio data from Redis
                portfolio_data = await self._get_portfolio_data()
                
                if portfolio_data:
                    # Analyze portfolio risk
                    portfolio_risk = await self._analyze_portfolio_risk(portfolio_data)
                    
                    if portfolio_risk:
                        self.stats["portfolio_analyses"] += 1
                        self.logger.log_portfolio_risk("main_portfolio", portfolio_risk)
                        
                        # Check for risk alerts
                        if portfolio_risk.get("risk_score", 0) > self.config.get("portfolio_risk_threshold", 0.7):
                            self.stats["risk_alerts"] += 1
                            self.logger.log_risk_alert("high_portfolio_risk", portfolio_risk)
                
                await asyncio.sleep(self.config.get("portfolio_monitoring_interval", 300))
                
            except Exception as e:
                self.logger.log_error(f"Error in portfolio monitoring loop: {e}")
                await asyncio.sleep(60)

    async def _risk_alert_loop(self):
        """Periodic risk alert monitoring loop."""
        while self.is_running:
            try:
                # Check for risk alerts
                alerts = await self._check_risk_alerts()
                
                if alerts:
                    for alert in alerts:
                        self.stats["risk_alerts"] += 1
                        self.logger.log_risk_alert(alert["type"], alert)
                
                await asyncio.sleep(self.config.get("risk_alert_interval", 30))
                
            except Exception as e:
                self.logger.log_error(f"Error in risk alert loop: {e}")
                await asyncio.sleep(15)

    async def _threshold_monitoring_loop(self):
        """Periodic threshold monitoring loop."""
        while self.is_running:
            try:
                # Check for threshold breaches
                breaches = await self._check_threshold_breaches()
                
                if breaches:
                    for breach in breaches:
                        self.stats["threshold_breaches"] += 1
                        self.logger.log_risk_threshold_breach(breach["type"], breach)
                
                await asyncio.sleep(self.config.get("threshold_monitoring_interval", 60))
                
            except Exception as e:
                self.logger.log_error(f"Error in threshold monitoring loop: {e}")
                await asyncio.sleep(30)

    async def _capital_allocation_loop(self):
        """Periodic capital allocation monitoring loop."""
        while self.is_running:
            try:
                # Monitor capital allocation
                allocation_data = await self._monitor_capital_allocation()
                
                if allocation_data:
                    self.logger.log_capital_allocation("allocation_monitoring", allocation_data)
                
                await asyncio.sleep(self.config.get("capital_allocation_interval", 600))
                
            except Exception as e:
                self.logger.log_error(f"Error in capital allocation loop: {e}")
                await asyncio.sleep(120)

    async def _stats_reporting_loop(self):
        """Periodic stats reporting loop."""
        while self.is_running:
            try:
                await self._report_stats()
                await asyncio.sleep(self.config.get("stats_interval", 300))
                
            except Exception as e:
                self.logger.log_error(f"Error in stats reporting loop: {e}")
                await asyncio.sleep(60)

    async def _get_strategy_data(self) -> pd.DataFrame:
        """Get strategy data from Redis."""
        try:
            if not self.redis_client:
                return pd.DataFrame()
            
            # Get strategy data from Redis
            strategy_keys = self.redis_client.keys("strategy:*")
            strategy_data = []
            
            for key in strategy_keys[:50]:  # Limit to 50 recent strategies
                try:
                    data = self.redis_client.hgetall(key)
                    if data:
                        strategy_data.append(data)
                except Exception as e:
                    self.logger.log_error(f"Error getting strategy data from {key}: {e}")
                    continue
            
            return pd.DataFrame(strategy_data)
            
        except Exception as e:
            self.logger.log_error(f"Error getting strategy data: {e}")
            return pd.DataFrame()

    async def _get_portfolio_data(self) -> Optional[Dict[str, Any]]:
        """Get portfolio data from Redis."""
        try:
            if not self.redis_client:
                return None
            
            # Get portfolio data from Redis
            portfolio_data = self.redis_client.hgetall("risk_management:portfolio")
            
            if portfolio_data:
                return portfolio_data
            else:
                # Return default portfolio data
                return {
                    "total_value": 100000.0,
                    "cash": 20000.0,
                    "positions": 80000.0,
                    "daily_pnl": 0.0,
                    "total_pnl": 0.0
                }
                
        except Exception as e:
            self.logger.log_error(f"Error getting portfolio data: {e}")
            return None

    async def _analyze_portfolio_risk(self, portfolio_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze portfolio risk."""
        try:
            total_value = float(portfolio_data.get("total_value", 100000.0))
            cash = float(portfolio_data.get("cash", 20000.0))
            positions = float(portfolio_data.get("positions", 80000.0))
            daily_pnl = float(portfolio_data.get("daily_pnl", 0.0))
            
            # Calculate risk metrics
            cash_ratio = cash / total_value if total_value > 0 else 0
            position_ratio = positions / total_value if total_value > 0 else 0
            daily_return = daily_pnl / total_value if total_value > 0 else 0
            
            # Risk score calculation
            risk_score = self._calculate_portfolio_risk_score(cash_ratio, position_ratio, daily_return)
            
            return {
                "total_value": total_value,
                "cash_ratio": cash_ratio,
                "position_ratio": position_ratio,
                "daily_return": daily_return,
                "risk_score": risk_score,
                "timestamp": int(time.time())
            }
            
        except Exception as e:
            self.logger.log_error(f"Error analyzing portfolio risk: {e}")
            return None

    def _calculate_portfolio_risk_score(self, cash_ratio: float, position_ratio: float, daily_return: float) -> float:
        """Calculate portfolio risk score."""
        try:
            # Cash ratio risk (lower cash = higher risk)
            cash_risk = max(0, 1 - cash_ratio)
            
            # Position ratio risk (higher positions = higher risk)
            position_risk = position_ratio
            
            # Daily return risk (negative returns = higher risk)
            return_risk = max(0, -daily_return) if daily_return < 0 else 0
            
            # Weighted risk score
            risk_score = (
                cash_risk * 0.3 +
                position_risk * 0.4 +
                return_risk * 0.3
            )
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            self.logger.log_error(f"Error calculating portfolio risk score: {e}")
            return 0.5

    async def _check_risk_alerts(self) -> List[Dict[str, Any]]:
        """Check for risk alerts."""
        try:
            alerts = []
            
            # Check daily loss limit
            if self.redis_client:
                daily_loss = self.redis_client.get("risk_management:daily_loss")
                if daily_loss:
                    current_loss = float(daily_loss)
                    max_daily_loss = self.config.get("max_daily_loss", 0.02)
                    
                    if current_loss > max_daily_loss:
                        alerts.append({
                            "type": "daily_loss_breach",
                            "current_loss": current_loss,
                            "max_loss": max_daily_loss,
                            "description": f"Daily loss {current_loss:.2%} exceeds limit {max_daily_loss:.2%}"
                        })
            
            # Check position concentration
            portfolio_data = await self._get_portfolio_data()
            if portfolio_data:
                position_ratio = float(portfolio_data.get("position_ratio", 0.0))
                max_position_ratio = self.config.get("max_position_ratio", 0.8)
                
                if position_ratio > max_position_ratio:
                    alerts.append({
                        "type": "position_concentration",
                        "position_ratio": position_ratio,
                        "max_ratio": max_position_ratio,
                        "description": f"Position ratio {position_ratio:.2%} exceeds limit {max_position_ratio:.2%}"
                    })
            
            return alerts
            
        except Exception as e:
            self.logger.log_error(f"Error checking risk alerts: {e}")
            return []

    async def _check_threshold_breaches(self) -> List[Dict[str, Any]]:
        """Check for threshold breaches."""
        try:
            breaches = []
            
            # Check risk threshold
            if self.redis_client:
                current_risk = self.redis_client.get("risk_management:current_risk")
                if current_risk:
                    risk_score = float(current_risk)
                    risk_threshold = self.config.get("risk_threshold", 0.05)
                    
                    if risk_score > risk_threshold:
                        breaches.append({
                            "type": "risk_threshold_breach",
                            "current_risk": risk_score,
                            "threshold": risk_threshold,
                            "description": f"Risk score {risk_score:.2f} exceeds threshold {risk_threshold:.2f}"
                        })
            
            return breaches
            
        except Exception as e:
            self.logger.log_error(f"Error checking threshold breaches: {e}")
            return []

    async def _monitor_capital_allocation(self) -> Optional[Dict[str, Any]]:
        """Monitor capital allocation."""
        try:
            portfolio_data = await self._get_portfolio_data()
            
            if portfolio_data:
                total_value = float(portfolio_data.get("total_value", 100000.0))
                cash = float(portfolio_data.get("cash", 20000.0))
                positions = float(portfolio_data.get("positions", 80000.0))
                
                return {
                    "total_value": total_value,
                    "cash_allocation": cash,
                    "position_allocation": positions,
                    "cash_ratio": cash / total_value if total_value > 0 else 0,
                    "position_ratio": positions / total_value if total_value > 0 else 0,
                    "timestamp": int(time.time())
                }
            
            return None
            
        except Exception as e:
            self.logger.log_error(f"Error monitoring capital allocation: {e}")
            return None

    async def _report_stats(self):
        """Report agent statistics."""
        try:
            uptime = time.time() - self.stats["start_time"]
            
            stats_report = {
                "uptime_seconds": uptime,
                "total_evaluations": self.stats["total_evaluations"],
                "approved_decisions": self.stats["approved_decisions"],
                "denied_decisions": self.stats["denied_decisions"],
                "approval_rate": (self.stats["approved_decisions"] / max(self.stats["total_evaluations"], 1)) * 100,
                "risk_alerts": self.stats["risk_alerts"],
                "threshold_breaches": self.stats["threshold_breaches"],
                "portfolio_analyses": self.stats["portfolio_analyses"],
                "evaluations_per_hour": self.stats["total_evaluations"] / max(uptime / 3600, 1),
                "last_evaluation_time": self.stats["last_evaluation_time"],
                "timestamp": time.time()
            }
            
            # Store stats in Redis
            if self.redis_client:
                self.redis_client.hset("risk_management:agent_stats", mapping=stats_report)
            
            # Log metrics
            self.logger.log_metric("total_evaluations", self.stats["total_evaluations"])
            self.logger.log_metric("approval_rate", stats_report["approval_rate"])
            self.logger.log_metric("risk_alerts", self.stats["risk_alerts"])
            
        except Exception as e:
            self.logger.log_error(f"Error reporting stats: {e}")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        uptime = time.time() - self.stats["start_time"]
        
        return {
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "stats": self.stats,
            "components": {
                "risk_core": hasattr(self, 'risk_core')
            }
        } 