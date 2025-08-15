#!/usr/bin/env python3
"""
Connection Manager - SIMPLIFIED CORE MODULE
Handles broker/exchange connections with 4-tier monitoring
SIMPLE: ~150 lines focused on connection management only
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from ...shared_utils import get_shared_logger

class ConnectionManager:
    """
    Simplified connection management engine.
    Focuses on essential connection monitoring and management.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("adapters", "connection_manager")
        
        # Connection state
        self.connections = {
            "ultra_hft": {},      # 1ms connections for arbitrage
            "fast": {},           # 100ms connections for market making
            "standard": {},       # 1s connections for standard strategies
            "backup": {}          # Backup connections
        }
        
        # Connection health tracking
        self.health_metrics = {
            "total_connections": 0,
            "active_connections": 0,
            "failed_connections": 0,
            "average_latency_ms": 0.0,
            "last_health_check": 0
        }
        
        # Broker configurations (simplified)
        self.broker_configs = {
            "exness_mt5": {
                "connection_type": "mt5",
                "latency_tier": "fast",
                "reliability": "high"
            },
            "binance": {
                "connection_type": "websocket",
                "latency_tier": "ultra_hft", 
                "reliability": "medium"
            }
        }
    
    async def initialize_connections(self):
        """Initialize broker connections."""
        try:
            self.logger.info("Initializing broker connections...")
            
            # Initialize each broker configuration
            for broker_name, config in self.broker_configs.items():
                await self._initialize_broker_connection(broker_name, config)
            
            # Update health metrics
            await self._update_health_metrics()
            
            self.logger.info(f"Initialized {self.health_metrics['active_connections']} connections")
            
        except Exception as e:
            self.logger.error(f"Error initializing connections: {e}")
    
    async def monitor_ultra_hft_connections(self):
        """Monitor ultra-HFT connections (1ms tier)."""
        try:
            # Check ultra-HFT connections
            for conn_id, connection in self.connections["ultra_hft"].items():
                await self._check_connection_health(conn_id, connection, "ultra_hft")
            
        except Exception as e:
            self.logger.warning(f"Error monitoring ultra-HFT connections: {e}")
    
    async def monitor_fast_connections(self):
        """Monitor fast connections (100ms tier)."""
        try:
            # Check fast connections
            for conn_id, connection in self.connections["fast"].items():
                await self._check_connection_health(conn_id, connection, "fast")
            
        except Exception as e:
            self.logger.warning(f"Error monitoring fast connections: {e}")
    
    async def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of all connections."""
        try:
            health_results = {
                "timestamp": time.time(),
                "active_connections": 0,
                "failed_connections": 0,
                "total_latency": 0.0,
                "connection_details": {}
            }
            
            # Check all connection tiers
            for tier_name, connections in self.connections.items():
                tier_health = await self._check_tier_health(tier_name, connections)
                health_results["connection_details"][tier_name] = tier_health
                
                health_results["active_connections"] += tier_health["active"]
                health_results["failed_connections"] += tier_health["failed"]
                health_results["total_latency"] += tier_health["total_latency"]
            
            # Calculate average latency
            total_connections = health_results["active_connections"] + health_results["failed_connections"]
            if total_connections > 0:
                health_results["average_latency_ms"] = health_results["total_latency"] / total_connections
            else:
                health_results["average_latency_ms"] = 0.0
            
            # Calculate health score
            if total_connections > 0:
                health_results["health_score"] = health_results["active_connections"] / total_connections
            else:
                health_results["health_score"] = 0.0
            
            # Update internal metrics
            self.health_metrics.update({
                "active_connections": health_results["active_connections"],
                "failed_connections": health_results["failed_connections"],
                "average_latency_ms": health_results["average_latency_ms"],
                "last_health_check": time.time()
            })
            
            return health_results
            
        except Exception as e:
            self.logger.warning(f"Error in health check: {e}")
            return {
                "error": str(e),
                "timestamp": time.time(),
                "active_connections": 0,
                "failed_connections": 1
            }
    
    async def execute_failover(self):
        """Execute failover to backup connections."""
        try:
            self.logger.warning("Executing connection failover...")
            
            # Move failed connections to backup
            failover_count = 0
            
            for tier_name, connections in self.connections.items():
                if tier_name == "backup":
                    continue
                    
                failed_connections = []
                for conn_id, connection in connections.items():
                    if not connection.get("is_healthy", False):
                        failed_connections.append(conn_id)
                
                # Move failed connections to backup tier
                for conn_id in failed_connections:
                    self.connections["backup"][conn_id] = self.connections[tier_name].pop(conn_id)
                    failover_count += 1
            
            self.logger.info(f"Failover completed: moved {failover_count} connections to backup")
            
            # Try to restore connections
            await self._attempt_connection_restoration()
            
        except Exception as e:
            self.logger.error(f"Error executing failover: {e}")
    
    async def close_all_connections(self):
        """Close all broker connections gracefully."""
        try:
            self.logger.info("Closing all connections...")
            
            total_closed = 0
            for tier_name, connections in self.connections.items():
                for conn_id, connection in connections.items():
                    await self._close_connection(conn_id, connection)
                    total_closed += 1
                connections.clear()
            
            self.logger.info(f"Closed {total_closed} connections")
            
        except Exception as e:
            self.logger.error(f"Error closing connections: {e}")
    
    # ============= PRIVATE CONNECTION METHODS =============
    
    async def _initialize_broker_connection(self, broker_name: str, config: Dict[str, Any]):
        """Initialize a specific broker connection."""
        try:
            # Simulate connection initialization
            connection = {
                "broker_name": broker_name,
                "connection_type": config.get("connection_type", "api"),
                "is_healthy": True,
                "latency_ms": self._simulate_latency(config.get("latency_tier", "standard")),
                "connected_at": time.time(),
                "last_ping": time.time()
            }
            
            # Add to appropriate tier
            tier = config.get("latency_tier", "standard")
            if tier == "ultra_hft":
                self.connections["ultra_hft"][broker_name] = connection
            elif tier == "fast":
                self.connections["fast"][broker_name] = connection
            else:
                self.connections["standard"][broker_name] = connection
            
            self.logger.info(f"Initialized {broker_name} connection in {tier} tier")
            
        except Exception as e:
            self.logger.warning(f"Error initializing {broker_name}: {e}")
    
    async def _check_connection_health(self, conn_id: str, connection: Dict[str, Any], tier: str):
        """Check health of a specific connection."""
        try:
            # Simulate health check
            await asyncio.sleep(0.001)  # 1ms health check
            
            # Update ping time
            connection["last_ping"] = time.time()
            
            # Simulate connection health (95% success rate)
            import random
            connection["is_healthy"] = random.random() > 0.05
            
            # Update latency
            connection["latency_ms"] = self._simulate_latency(tier)
            
        except Exception as e:
            self.logger.warning(f"Error checking health of {conn_id}: {e}")
            connection["is_healthy"] = False
    
    async def _check_tier_health(self, tier_name: str, connections: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of all connections in a tier."""
        try:
            tier_health = {
                "tier": tier_name,
                "active": 0,
                "failed": 0,
                "total_latency": 0.0
            }
            
            for conn_id, connection in connections.items():
                if connection.get("is_healthy", False):
                    tier_health["active"] += 1
                else:
                    tier_health["failed"] += 1
                
                tier_health["total_latency"] += connection.get("latency_ms", 0.0)
            
            return tier_health
            
        except Exception as e:
            self.logger.warning(f"Error checking tier health for {tier_name}: {e}")
            return {"tier": tier_name, "active": 0, "failed": 1, "total_latency": 0.0}
    
    async def _attempt_connection_restoration(self):
        """Attempt to restore failed connections."""
        try:
            # Try to restore backup connections
            restored_count = 0
            
            for conn_id, connection in list(self.connections["backup"].items()):
                # Simulate restoration attempt (70% success rate)
                import random
                if random.random() > 0.3:
                    connection["is_healthy"] = True
                    connection["last_ping"] = time.time()
                    
                    # Move back to appropriate tier
                    original_tier = "fast"  # Default tier for restored connections
                    self.connections[original_tier][conn_id] = self.connections["backup"].pop(conn_id)
                    restored_count += 1
            
            if restored_count > 0:
                self.logger.info(f"Restored {restored_count} connections")
            
        except Exception as e:
            self.logger.warning(f"Error attempting connection restoration: {e}")
    
    async def _close_connection(self, conn_id: str, connection: Dict[str, Any]):
        """Close a specific connection."""
        try:
            # Simulate connection closure
            connection["is_healthy"] = False
            connection["closed_at"] = time.time()
            
        except Exception as e:
            self.logger.warning(f"Error closing connection {conn_id}: {e}")
    
    async def _update_health_metrics(self):
        """Update overall health metrics."""
        try:
            total_connections = 0
            active_connections = 0
            
            for tier_connections in self.connections.values():
                for connection in tier_connections.values():
                    total_connections += 1
                    if connection.get("is_healthy", False):
                        active_connections += 1
            
            self.health_metrics.update({
                "total_connections": total_connections,
                "active_connections": active_connections,
                "failed_connections": total_connections - active_connections
            })
            
        except Exception as e:
            self.logger.warning(f"Error updating health metrics: {e}")
    
    def _simulate_latency(self, tier: str) -> float:
        """Simulate connection latency based on tier."""
        latency_ranges = {
            "ultra_hft": (0.5, 2.0),      # 0.5-2ms
            "fast": (50, 150),            # 50-150ms
            "standard": (500, 1500),      # 500-1500ms
            "backup": (1000, 3000)        # 1-3s
        }
        
        import random
        min_latency, max_latency = latency_ranges.get(tier, (100, 500))
        return random.uniform(min_latency, max_latency)
    
    # ============= UTILITY METHODS =============
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status."""
        return {
            "health_metrics": self.health_metrics,
            "connections_by_tier": {
                tier: len(connections) for tier, connections in self.connections.items()
            },
            "connection_details": self.connections
        }
    
    async def create_connection_pool(self, pool_type: str = None, config: Dict[str, Any] = None):
        """Create connection pools for different tiers."""
        try:
            self.logger.info("✅ Connection pools created")
            self.logger.info(f"✅ Pool configurations: {len(self.broker_configs)} brokers")
            
            # Initialize connection pools for each tier
            for tier in self.connections.keys():
                if tier not in self.connections:
                    self.connections[tier] = {}
                self.logger.info(f"✅ {tier} tier pool initialized")
            
            # Create broker-specific connection pools
            for broker_name, config in self.broker_configs.items():
                tier = config.get("latency_tier", "standard")
                pool_id = f"{broker_name}_pool"
                
                self.connections[tier][pool_id] = {
                    "broker": broker_name,
                    "pool_size": 5,
                    "active_connections": 0,
                    "max_connections": 10,
                    "created_at": time.time(),
                    "is_healthy": True
                }
                
                self.logger.info(f"✅ Created {broker_name} connection pool in {tier} tier")
            
        except Exception as e:
            self.logger.error(f"❌ Error creating connection pools: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup connection manager resources."""
        try:
            self.logger.info("Cleaning up connection manager resources...")
            
            # Close all connections
            for tier, connections in self.connections.items():
                for conn_id, connection in connections.items():
                    # Mark connection as closed
                    connection["is_healthy"] = False
                    connection["status"] = "closed"
                
                # Clear connections
                connections.clear()
            
            # Reset health metrics
            self.health_metrics = {
                "total_connections": 0,
                "active_connections": 0,
                "failed_connections": 0,
                "average_latency_ms": 0.0,
                "last_health_check": 0
            }
            
            self.logger.info("✅ Connection manager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during connection manager cleanup: {e}")
            raise
    
    async def get_pool_status(self) -> Dict[str, Any]:
        """Get connection pool status."""
        try:
            pool_status = {}
            
            for tier, connections in self.connections.items():
                pool_status[tier] = {
                    "total_connections": len(connections),
                    "active_connections": sum(1 for conn in connections.values() if conn.get("is_healthy", False)),
                    "connections": list(connections.keys())
                }
            
            return {
                "timestamp": time.time(),
                "pool_status": pool_status,
                "overall_health": self.health_metrics,
                "total_pools": len(self.connections)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting pool status: {e}")
            return {
                "timestamp": time.time(),
                "pool_status": {},
                "error": str(e)
            }
