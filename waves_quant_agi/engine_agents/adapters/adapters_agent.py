import asyncio
import time
from typing import Dict, Any, Optional, List
import redis
from .logs.broker_logger import BrokerLogger
from .broker_integrations.binance_adapter import BinanceAdapter

from .broker_integrations.exness_adapter import ExnessAdapter
from .router.broker_router import BrokerRouter
from .normalizer.order_normalizer import OrderNormalizer
from .status_monitor.health_checker import HealthChecker
from .status_monitor.performance_tracker import PerformanceTracker
from .retry_engine.retry_handler import RetryHandler
from .learning_layer.pattern_analyzer import PatternAnalyzer
from .learning_layer.broker_intelligence import BrokerIntelligence
from .broker_updater.api_monitor import APIMonitor

class AdaptersAgent:
    """Main orchestrator for all broker adapters with intelligent routing and monitoring."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        
        # Initialize Redis connection
        self.redis_client = self._init_redis()
        self.logger = BrokerLogger("adapters_agent", self.redis_client)
        
        # Initialize core components
        self.router = BrokerRouter(config.get("router", {}))
        self.order_normalizer = OrderNormalizer()
        self.health_checker = HealthChecker()
        self.performance_tracker = PerformanceTracker()
        self.retry_handler = RetryHandler()
        self.pattern_analyzer = PatternAnalyzer()
        self.broker_intelligence = BrokerIntelligence()
        self.api_monitor = APIMonitor()
        
        # Initialize broker adapters
        self._init_broker_adapters()
        
        # Performance tracking
        self.stats = {
            "total_orders_processed": 0,
            "successful_orders": 0,
            "failed_orders": 0,
            "total_volume_processed": 0.0,
            "last_order_time": 0,
            "start_time": time.time()
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

    def _init_broker_adapters(self):
        """Initialize broker adapters based on configuration."""
        try:
            broker_configs = self.config.get("brokers", {})
            
            # Initialize Binance adapter
            if "binance" in broker_configs:
                binance_config = broker_configs["binance"]
                binance_adapter = BinanceAdapter(
                    api_key=binance_config.get("api_key", ""),
                    api_secret=binance_config.get("api_secret", ""),
                    config=binance_config
                )
                self.router.add_adapter("binance", binance_adapter)
                self.logger.log("Binance adapter initialized")
            

            
            # Initialize Exness adapter
            if "exness" in broker_configs:
                exness_config = broker_configs["exness"]
                exness_adapter = ExnessAdapter(
                    api_key=exness_config.get("api_key", ""),
                    api_secret=exness_config.get("api_secret", ""),
                    config=exness_config
                )
                self.router.add_adapter("exness", exness_adapter)
                self.logger.log("Exness adapter initialized")
            
            self.logger.log(f"Initialized {len(self.router.get_available_brokers())} broker adapters")
            
        except Exception as e:
            self.logger.log_error(f"Error initializing broker adapters: {e}")

    async def start(self):
        """Start the adapters agent."""
        try:
            self.logger.log("Starting Adapters Agent...")
            self.is_running = True
            
            # Connect to all brokers
            await self._connect_all_brokers()
            
            # Start monitoring tasks
            tasks = [
                asyncio.create_task(self._health_check_loop()),
                asyncio.create_task(self._performance_monitoring_loop()),
                asyncio.create_task(self._pattern_analysis_loop()),
                asyncio.create_task(self._api_monitoring_loop()),
                asyncio.create_task(self._stats_reporting_loop())
            ]
            
            # Start all tasks
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logger.log_error(f"Error starting adapters agent: {e}")
            await self.stop()

    async def stop(self):
        """Stop the adapters agent gracefully."""
        self.logger.log("Stopping Adapters Agent...")
        self.is_running = False
        
        try:
            # Disconnect from all brokers
            await self._disconnect_all_brokers()
            
            self.logger.log("Adapters Agent stopped successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error stopping adapters agent: {e}")

    async def _connect_all_brokers(self):
        """Connect to all broker adapters."""
        try:
            connection_status = await self.router.check_all_connections()
            
            connected_count = sum(1 for status in connection_status.values() if status)
            total_count = len(connection_status)
            
            self.logger.log(f"Connected to {connected_count}/{total_count} brokers")
            
            # Store connection status in Redis
            if self.redis_client:
                try:
                    status_data = {
                        "timestamp": time.time(),
                        "connections": connection_status,
                        "connected_count": connected_count,
                        "total_count": total_count
                    }
                    
                    status_key = "adapters:connection_status"
                    self.redis_client.hset(status_key, mapping=status_data)
                    self.redis_client.expire(status_key, 300)  # 5 minutes
                except Exception as e:
                    self.logger.log_error(f"Failed to store connection status: {e}")
                    
        except Exception as e:
            self.logger.log_error(f"Error connecting to brokers: {e}")

    async def _disconnect_all_brokers(self):
        """Disconnect from all broker adapters."""
        try:
            for broker_name, adapter in self.router.adapters.items():
                try:
                    await adapter.disconnect()
                    self.logger.log(f"Disconnected from {broker_name}")
                except Exception as e:
                    self.logger.log_error(f"Error disconnecting from {broker_name}: {e}")
                    
        except Exception as e:
            self.logger.log_error(f"Error disconnecting from brokers: {e}")

    async def execute_order(self, order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute an order through the broker router."""
        try:
            # Normalize order
            normalized_order = self.order_normalizer.normalize(order)
            
            # Update stats
            self.stats["total_orders_processed"] += 1
            self.stats["last_order_time"] = time.time()
            
            # Execute order with retry logic
            response = await self.retry_handler.execute_with_retry(
                lambda: self.router.route_order_with_fallback(normalized_order),
                max_retries=self.config.get("max_retries", 3)
            )
            
            if response:
                self.stats["successful_orders"] += 1
                volume = float(order.get("amount", 0)) * float(order.get("price", 0))
                self.stats["total_volume_processed"] += volume
                
                # Record successful execution
                self.performance_tracker.record_successful_order(
                    response.get("broker", "unknown"),
                    volume,
                    response.get("execution_time", 0)
                )
                
                self.logger.log_order(
                    response.get("broker", "unknown"),
                    order,
                    "executed_successfully",
                    response.get("id")
                )
                
                return response
            else:
                self.stats["failed_orders"] += 1
                
                # Record failed execution
                self.performance_tracker.record_failed_order(
                    "unknown",
                    volume=0
                )
                
                self.logger.log_order("unknown", order, "execution_failed")
                return None
                
        except Exception as e:
            self.stats["failed_orders"] += 1
            self.logger.log_error(f"Error executing order: {e}", {"order": order})
            return None

    async def _health_check_loop(self):
        """Periodic health check loop."""
        while self.is_running:
            try:
                # Check broker connections
                connection_status = await self.router.check_all_connections()
                
                # Update health checker
                self.health_checker.update_connection_status(connection_status)
                
                # Check for unhealthy brokers
                unhealthy_brokers = self.health_checker.get_unhealthy_brokers()
                if unhealthy_brokers:
                    self.logger.log_error(f"Unhealthy brokers detected: {unhealthy_brokers}")
                
                await asyncio.sleep(self.config.get("health_check_interval", 30))
                
            except Exception as e:
                self.logger.log_error(f"Error in health check loop: {e}")
                await asyncio.sleep(10)

    async def _performance_monitoring_loop(self):
        """Periodic performance monitoring loop."""
        while self.is_running:
            try:
                # Update performance metrics
                broker_stats = self.router.get_broker_stats()
                self.performance_tracker.update_broker_metrics(broker_stats)
                
                # Check for performance issues
                performance_issues = self.performance_tracker.get_performance_issues()
                if performance_issues:
                    self.logger.log_error(f"Performance issues detected: {performance_issues}")
                
                await asyncio.sleep(self.config.get("performance_monitoring_interval", 60))
                
            except Exception as e:
                self.logger.log_error(f"Error in performance monitoring loop: {e}")
                await asyncio.sleep(10)

    async def _pattern_analysis_loop(self):
        """Periodic pattern analysis loop."""
        while self.is_running:
            try:
                # Analyze order patterns
                order_patterns = self.pattern_analyzer.analyze_patterns()
                
                # Update broker intelligence
                self.broker_intelligence.update_patterns(order_patterns)
                
                # Get intelligence insights
                insights = self.broker_intelligence.get_insights()
                if insights:
                    self.logger.log(f"Broker intelligence insights: {insights}")
                
                await asyncio.sleep(self.config.get("pattern_analysis_interval", 300))
                
            except Exception as e:
                self.logger.log_error(f"Error in pattern analysis loop: {e}")
                await asyncio.sleep(30)

    async def _api_monitoring_loop(self):
        """Periodic API monitoring loop."""
        while self.is_running:
            try:
                # Monitor API usage
                api_metrics = self.api_monitor.get_api_metrics()
                
                # Check for API limits
                api_issues = self.api_monitor.check_api_limits()
                if api_issues:
                    self.logger.log_error(f"API issues detected: {api_issues}")
                
                await asyncio.sleep(self.config.get("api_monitoring_interval", 60))
                
            except Exception as e:
                self.logger.log_error(f"Error in API monitoring loop: {e}")
                await asyncio.sleep(10)

    async def _stats_reporting_loop(self):
        """Periodic stats reporting loop."""
        while self.is_running:
            try:
                await self._report_stats()
                await asyncio.sleep(self.config.get("stats_interval", 60))
                
            except Exception as e:
                self.logger.log_error(f"Error in stats reporting loop: {e}")
                await asyncio.sleep(30)

    async def _report_stats(self):
        """Report agent statistics."""
        try:
            uptime = time.time() - self.stats["start_time"]
            
            stats_report = {
                "uptime_seconds": uptime,
                "total_orders_processed": self.stats["total_orders_processed"],
                "successful_orders": self.stats["successful_orders"],
                "failed_orders": self.stats["failed_orders"],
                "success_rate": (self.stats["successful_orders"] / max(self.stats["total_orders_processed"], 1)) * 100,
                "total_volume_processed": self.stats["total_volume_processed"],
                "orders_per_second": self.stats["total_orders_processed"] / max(uptime, 1),
                "last_order_time": self.stats["last_order_time"],
                "timestamp": time.time()
            }
            
            # Store stats in Redis
            if self.redis_client:
                self.redis_client.hset("adapters:stats", mapping=stats_report)
            
            # Log metrics
            self.logger.log_metric("total_orders_processed", self.stats["total_orders_processed"])
            self.logger.log_metric("success_rate", stats_report["success_rate"])
            
        except Exception as e:
            self.logger.log_error(f"Error reporting stats: {e}")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        uptime = time.time() - self.stats["start_time"]
        
        return {
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "stats": self.stats,
            "router_stats": self.router.get_stats(),
            "broker_stats": self.router.get_broker_stats(),
            "health_status": self.health_checker.get_health_status(),
            "performance_status": self.performance_tracker.get_performance_status(),
            "available_brokers": self.router.get_available_brokers(),
            "available_strategies": self.router.get_available_strategies()
        } 