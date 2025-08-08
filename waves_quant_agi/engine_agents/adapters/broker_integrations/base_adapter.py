from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import time
import redis
from ..logs.broker_logger import BrokerLogger

class BaseAdapter(ABC):
    """Base class for all broker adapters with common functionality."""
    
    def __init__(self, broker_name: str, api_key: str, api_secret: str, config: Optional[Dict[str, Any]] = None):
        self.broker_name = broker_name
        self.api_key = api_key
        self.api_secret = api_secret
        self.config = config or {}
        
        # Initialize Redis connection
        self.redis_client = self._init_redis()
        self.logger = BrokerLogger(broker_name, self.redis_client)
        
        # Performance tracking
        self.stats = {
            "total_orders": 0,
            "successful_orders": 0,
            "failed_orders": 0,
            "total_volume": 0.0,
            "last_order_time": 0,
            "start_time": time.time()
        }
        
        # Connection status
        self.is_connected = False
        self.last_heartbeat = 0
        self.connection_errors = 0

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

    @abstractmethod
    def format_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Format internal order to broker-specific format."""
        pass

    @abstractmethod
    async def send_order(self, formatted_order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send order to broker and return response."""
        pass

    @abstractmethod
    def confirm_order(self, order_id: str) -> bool:
        """Confirm if order was accepted by broker."""
        pass

    @abstractmethod
    def handle_broker_quirks(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """Handle broker-specific quirks (e.g., decimal limits, KYC)."""
        pass

    async def connect(self) -> bool:
        """Establish connection to broker."""
        try:
            # Implement connection logic in subclasses
            self.is_connected = True
            self.last_heartbeat = time.time()
            self.connection_errors = 0
            self.logger.log_connection_status(self.broker_name, "connected")
            return True
        except Exception as e:
            self.is_connected = False
            self.connection_errors += 1
            self.logger.log_connection_status(self.broker_name, "failed", str(e))
            return False

    async def disconnect(self):
        """Disconnect from broker."""
        try:
            self.is_connected = False
            self.logger.log_connection_status(self.broker_name, "disconnected")
        except Exception as e:
            self.logger.log_error(f"Error disconnecting from {self.broker_name}: {e}")

    async def check_connection(self) -> bool:
        """Check if connection to broker is healthy."""
        try:
            # Implement health check in subclasses
            self.last_heartbeat = time.time()
            return self.is_connected
        except Exception as e:
            self.is_connected = False
            self.connection_errors += 1
            self.logger.log_error(f"Connection check failed for {self.broker_name}: {e}")
            return False

    async def execute_order(self, order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute an order with comprehensive error handling and logging."""
        try:
            # Check connection
            if not await self.check_connection():
                self.logger.log_error(f"Not connected to {self.broker_name}")
                return None
            
            # Format order
            formatted_order = self.format_order(order)
            self.logger.log_request(self.broker_name, {"original": order, "formatted": formatted_order})
            
            # Send order
            start_time = time.time()
            response = await self.send_order(formatted_order)
            execution_time = time.time() - start_time
            
            # Update stats
            self.stats["total_orders"] += 1
            self.stats["last_order_time"] = time.time()
            
            if response:
                self.stats["successful_orders"] += 1
                volume = float(order.get("amount", 0)) * float(order.get("price", 0))
                self.stats["total_volume"] += volume
                
                self.logger.log_order(
                    self.broker_name, 
                    order, 
                    "success", 
                    response.get("id")
                )
                
                self.logger.log_metric("order_execution_time", execution_time, {
                    "broker": self.broker_name,
                    "symbol": order.get("symbol", "unknown")
                })
                
                # Store order in Redis
                if self.redis_client:
                    try:
                        order_data = {
                            "broker": self.broker_name,
                            "order": order,
                            "response": response,
                            "execution_time": execution_time,
                            "timestamp": time.time()
                        }
                        
                        order_key = f"broker_adapters:executed_orders:{int(time.time())}"
                        self.redis_client.hset(order_key, mapping=order_data)
                        self.redis_client.expire(order_key, 86400)  # 24 hours
                    except Exception as e:
                        self.logger.log_error(f"Failed to store order in Redis: {e}")
                
                return response
            else:
                self.stats["failed_orders"] += 1
                self.logger.log_order(self.broker_name, order, "failed")
                return None
                
        except Exception as e:
            self.stats["failed_orders"] += 1
            self.logger.log_error(f"Error executing order on {self.broker_name}: {e}", {
                "order": order,
                "broker": self.broker_name
            })
            return None

    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get account information from broker."""
        try:
            # Implement in subclasses
            return None
        except Exception as e:
            self.logger.log_error(f"Error getting account info from {self.broker_name}: {e}")
            return None

    def get_balance(self, currency: str = "USD") -> Optional[float]:
        """Get account balance for specific currency."""
        try:
            account_info = self.get_account_info()
            if account_info and "balances" in account_info:
                for balance in account_info["balances"]:
                    if balance.get("currency") == currency:
                        return float(balance.get("free", 0))
            return None
        except Exception as e:
            self.logger.log_error(f"Error getting balance from {self.broker_name}: {e}")
            return None

    def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific order."""
        try:
            # Implement in subclasses
            return None
        except Exception as e:
            self.logger.log_error(f"Error getting order status from {self.broker_name}: {e}")
            return None

    def cancel_order(self, order_id: str) -> bool:
        """Cancel a specific order."""
        try:
            # Implement in subclasses
            return False
        except Exception as e:
            self.logger.log_error(f"Error canceling order on {self.broker_name}: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics."""
        uptime = time.time() - self.stats["start_time"]
        total_orders = self.stats["successful_orders"] + self.stats["failed_orders"]
        
        return {
            "broker_name": self.broker_name,
            "is_connected": self.is_connected,
            "uptime_seconds": uptime,
            "total_orders": total_orders,
            "successful_orders": self.stats["successful_orders"],
            "failed_orders": self.stats["failed_orders"],
            "success_rate": (self.stats["successful_orders"] / max(total_orders, 1)) * 100,
            "total_volume": self.stats["total_volume"],
            "orders_per_second": total_orders / max(uptime, 1),
            "last_order_time": self.stats["last_order_time"],
            "connection_errors": self.connection_errors,
            "last_heartbeat": self.last_heartbeat
        }

    def log_request(self, request: Dict[str, Any], response: Optional[Dict[str, Any]] = None):
        """Log request and response details."""
        self.logger.log_request(self.broker_name, request, response)