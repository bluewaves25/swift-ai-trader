#!/usr/bin/env python3
"""
Redis Channel Manager for 4-Tier Trading Engine
Manages all inter-agent communication with proper routing and QoS
"""

import asyncio
import redis
import json
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging
from .message_formats import MessageFormat, MessagePriority, MessageType, validate_message_format

class ChannelType(Enum):
    """Redis channel types for different tiers."""
    HFT_SIGNALS = "hft_signals"                    # Ultra-HFT (1ms-10ms)
    FAST_SIGNALS = "fast_signals"                  # Fast execution (100ms-1s)
    TACTICAL_SIGNALS = "tactical_signals"          # Tactical analysis (1s-60s)
    STRATEGIC_SIGNALS = "strategic_signals"        # Strategic coordination (1min+)
    
    # Direct agent channels
    STRATEGY_ENGINE_ALERTS = "strategy_engine_alerts"
    RISK_MANAGEMENT_ALERTS = "risk_management_alerts"
    EXECUTION_ALERTS = "execution_alerts"
    INTELLIGENCE_ALERTS = "intelligence_alerts"
    
    # System channels
    MARKET_ANOMALIES = "market_anomalies"
    SYSTEM_HEALTH = "system_health"
    AGENT_STATUS = "agent_status"
    ERROR_ALERTS = "error_alerts"

@dataclass
class ChannelConfig:
    """Configuration for Redis channels."""
    name: str
    priority: MessagePriority
    max_message_age_ms: int     # Maximum age before message expires
    max_queue_size: int         # Maximum messages in queue
    qos_enabled: bool           # Quality of Service enabled
    batch_size: int             # Batch size for processing
    retry_count: int            # Retry attempts for failed delivery

class RedisChannelManager:
    """Manages Redis channels for all agent communication."""
    
    def __init__(self, redis_config: Dict[str, Any]):
        self.redis_config = redis_config
        self.redis_client = None
        self.pubsub = None
        self.is_running = False
        
        # Channel configurations
        self.channel_configs = self._init_channel_configs()
        
        # Message handlers
        self.message_handlers: Dict[str, List[Callable]] = {}
        
        # QoS metrics
        self.qos_metrics = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_dropped": 0,
            "average_latency_ms": 0.0,
            "channel_stats": {}
        }
        
        # Setup logging
        self.logger = logging.getLogger("redis_channel_manager")
    
    def _init_channel_configs(self) -> Dict[ChannelType, ChannelConfig]:
        """Initialize channel configurations with QoS settings."""
        return {
            # TIER 1: Ultra-HFT Channels (Critical priority)
            ChannelType.HFT_SIGNALS: ChannelConfig(
                name="hft_signals",
                priority=MessagePriority.CRITICAL,
                max_message_age_ms=10,      # 10ms max age
                max_queue_size=100,         # Small queue for speed
                qos_enabled=True,
                batch_size=1,               # No batching for HFT
                retry_count=0               # No retries for HFT
            ),
            
            # TIER 2: Fast Execution Channels (High priority)
            ChannelType.FAST_SIGNALS: ChannelConfig(
                name="fast_signals",
                priority=MessagePriority.HIGH,
                max_message_age_ms=1000,    # 1s max age
                max_queue_size=500,
                qos_enabled=True,
                batch_size=10,              # Small batches
                retry_count=1
            ),
            
            # TIER 3: Tactical Channels (Medium priority)
            ChannelType.TACTICAL_SIGNALS: ChannelConfig(
                name="tactical_signals",
                priority=MessagePriority.MEDIUM,
                max_message_age_ms=30000,   # 30s max age
                max_queue_size=1000,
                qos_enabled=True,
                batch_size=50,              # Medium batches
                retry_count=2
            ),
            
            # TIER 4: Strategic Channels (Low priority)
            ChannelType.STRATEGIC_SIGNALS: ChannelConfig(
                name="strategic_signals",
                priority=MessagePriority.LOW,
                max_message_age_ms=300000,  # 5min max age
                max_queue_size=2000,
                qos_enabled=False,          # Best effort
                batch_size=100,             # Large batches
                retry_count=3
            ),
            
            # Direct Agent Channels
            ChannelType.STRATEGY_ENGINE_ALERTS: ChannelConfig(
                name="strategy_engine_alerts",
                priority=MessagePriority.HIGH,
                max_message_age_ms=5000,
                max_queue_size=200,
                qos_enabled=True,
                batch_size=5,
                retry_count=1
            ),
            
            ChannelType.RISK_MANAGEMENT_ALERTS: ChannelConfig(
                name="risk_management_alerts",
                priority=MessagePriority.HIGH,
                max_message_age_ms=2000,
                max_queue_size=200,
                qos_enabled=True,
                batch_size=5,
                retry_count=1
            ),
            
            ChannelType.EXECUTION_ALERTS: ChannelConfig(
                name="execution_alerts",
                priority=MessagePriority.CRITICAL,
                max_message_age_ms=100,
                max_queue_size=100,
                qos_enabled=True,
                batch_size=1,
                retry_count=0
            ),
            
            ChannelType.INTELLIGENCE_ALERTS: ChannelConfig(
                name="intelligence_alerts",
                priority=MessagePriority.HIGH,
                max_message_age_ms=5000,
                max_queue_size=200,
                qos_enabled=True,
                batch_size=5,
                retry_count=1
            ),
            
            # System Channels
            ChannelType.MARKET_ANOMALIES: ChannelConfig(
                name="market_anomalies",
                priority=MessagePriority.HIGH,
                max_message_age_ms=1000,
                max_queue_size=500,
                qos_enabled=True,
                batch_size=1,               # Immediate broadcast
                retry_count=2
            ),
            
            ChannelType.SYSTEM_HEALTH: ChannelConfig(
                name="system_health",
                priority=MessagePriority.MEDIUM,
                max_message_age_ms=60000,
                max_queue_size=100,
                qos_enabled=False,
                batch_size=10,
                retry_count=1
            ),
            
            ChannelType.AGENT_STATUS: ChannelConfig(
                name="agent_status",
                priority=MessagePriority.LOW,
                max_message_age_ms=30000,
                max_queue_size=50,
                qos_enabled=False,
                batch_size=5,
                retry_count=0
            ),
            
            ChannelType.ERROR_ALERTS: ChannelConfig(
                name="error_alerts",
                priority=MessagePriority.CRITICAL,
                max_message_age_ms=5000,
                max_queue_size=100,
                qos_enabled=True,
                batch_size=1,
                retry_count=2
            )
        }
    
    async def initialize(self) -> bool:
        """Initialize Redis connection and pubsub."""
        try:
            # Initialize Redis client
            self.redis_client = redis.Redis(
                host=self.redis_config.get("redis_host", "localhost"),
                port=self.redis_config.get("redis_port", 6379),
                db=self.redis_config.get("redis_db", 0),
                decode_responses=True
            )
            
            # Test connection
            await asyncio.get_event_loop().run_in_executor(None, self.redis_client.ping)
            
            # Initialize pubsub
            self.pubsub = self.redis_client.pubsub()
            
            # Initialize channel stats
            for channel_type in ChannelType:
                self.qos_metrics["channel_stats"][channel_type.value] = {
                    "messages_sent": 0,
                    "messages_received": 0,
                    "average_latency_ms": 0.0,
                    "queue_size": 0,
                    "dropped_messages": 0
                }
            
            self.logger.info("Redis Channel Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis Channel Manager: {e}")
            return False
    
    async def start(self) -> None:
        """Start the channel manager."""
        if not await self.initialize():
            raise Exception("Failed to initialize Redis Channel Manager")
        
        self.is_running = True
        self.logger.info("Redis Channel Manager started")
        
        # Start background tasks
        asyncio.create_task(self._qos_monitor_loop())
        asyncio.create_task(self._message_cleanup_loop())
        asyncio.create_task(self._channel_health_monitor())
    
    async def stop(self) -> None:
        """Stop the channel manager."""
        self.is_running = False
        
        if self.pubsub:
            await asyncio.get_event_loop().run_in_executor(None, self.pubsub.close)
        
        if self.redis_client:
            await asyncio.get_event_loop().run_in_executor(None, self.redis_client.close)
        
        self.logger.info("Redis Channel Manager stopped")
    
    async def publish_message(self, channel: ChannelType, message: MessageFormat) -> bool:
        """Publish message to specified channel with QoS."""
        try:
            channel_config = self.channel_configs[channel]
            
            # Validate message format
            message_dict = message.to_dict()
            if not validate_message_format(message_dict):
                self.logger.error(f"Invalid message format for channel {channel.value}")
                return False
            
            # Check message age for HFT channels
            if channel_config.priority == MessagePriority.CRITICAL:
                age_ms = (time.time() - message.timestamp) * 1000
                if age_ms > channel_config.max_message_age_ms:
                    self.qos_metrics["messages_dropped"] += 1
                    self.qos_metrics["channel_stats"][channel.value]["dropped_messages"] += 1
                    self.logger.warning(f"Dropping aged HFT message: {age_ms}ms old")
                    return False
            
            # Add QoS metadata
            message_dict["qos_metadata"] = {
                "channel": channel.value,
                "priority": channel_config.priority.value,
                "sent_at": time.time(),
                "max_age_ms": channel_config.max_message_age_ms,
                "retry_count": 0,
                "max_retries": channel_config.retry_count
            }
            
            # Publish message
            message_json = json.dumps(message_dict)
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.publish, channel_config.name, message_json
            )
            
            # Update metrics
            self.qos_metrics["messages_sent"] += 1
            self.qos_metrics["channel_stats"][channel.value]["messages_sent"] += 1
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to publish message to {channel.value}: {e}")
            return False
    
    async def subscribe_to_channel(self, channel: ChannelType, 
                                 handler: Callable[[Dict[str, Any]], None]) -> bool:
        """Subscribe to channel with message handler."""
        try:
            channel_config = self.channel_configs[channel]
            
            # Add handler
            if channel.value not in self.message_handlers:
                self.message_handlers[channel.value] = []
            self.message_handlers[channel.value].append(handler)
            
            # Subscribe to Redis channel
            await asyncio.get_event_loop().run_in_executor(
                None, self.pubsub.subscribe, channel_config.name
            )
            
            self.logger.info(f"Subscribed to channel {channel.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to subscribe to channel {channel.value}: {e}")
            return False
    
    async def unsubscribe_from_channel(self, channel: ChannelType) -> bool:
        """Unsubscribe from channel."""
        try:
            channel_config = self.channel_configs[channel]
            
            # Unsubscribe from Redis channel
            await asyncio.get_event_loop().run_in_executor(
                None, self.pubsub.unsubscribe, channel_config.name
            )
            
            # Remove handlers
            if channel.value in self.message_handlers:
                del self.message_handlers[channel.value]
            
            self.logger.info(f"Unsubscribed from channel {channel.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unsubscribe from channel {channel.value}: {e}")
            return False
    
    async def listen_for_messages(self) -> None:
        """Listen for incoming messages and route to handlers."""
        try:
            while self.is_running:
                # Get message from pubsub
                message = await asyncio.get_event_loop().run_in_executor(
                    None, self.pubsub.get_message, True, 0.1
                )
                
                if message and message['type'] == 'message':
                    await self._process_incoming_message(message)
                
                await asyncio.sleep(0.001)  # Small delay to prevent CPU spinning
                
        except Exception as e:
            self.logger.error(f"Error in message listener: {e}")
    
    async def _process_incoming_message(self, redis_message: Dict[str, Any]) -> None:
        """Process incoming message with QoS validation."""
        try:
            channel_name = redis_message['channel']
            message_data = json.loads(redis_message['data'])
            
            # Validate message format
            if not validate_message_format(message_data):
                self.logger.error(f"Received invalid message format on {channel_name}")
                return
            
            # Check message age
            qos_metadata = message_data.get("qos_metadata", {})
            sent_at = qos_metadata.get("sent_at", time.time())
            age_ms = (time.time() - sent_at) * 1000
            max_age_ms = qos_metadata.get("max_age_ms", 60000)
            
            if age_ms > max_age_ms:
                self.qos_metrics["messages_dropped"] += 1
                if channel_name in self.qos_metrics["channel_stats"]:
                    self.qos_metrics["channel_stats"][channel_name]["dropped_messages"] += 1
                self.logger.warning(f"Dropping aged message on {channel_name}: {age_ms}ms old")
                return
            
            # Update metrics
            self.qos_metrics["messages_received"] += 1
            if channel_name in self.qos_metrics["channel_stats"]:
                self.qos_metrics["channel_stats"][channel_name]["messages_received"] += 1
                # Update average latency
                current_latency = self.qos_metrics["channel_stats"][channel_name]["average_latency_ms"]
                new_latency = (current_latency + age_ms) / 2
                self.qos_metrics["channel_stats"][channel_name]["average_latency_ms"] = new_latency
            
            # Route to handlers
            if channel_name in self.message_handlers:
                for handler in self.message_handlers[channel_name]:
                    try:
                        await asyncio.get_event_loop().run_in_executor(
                            None, handler, message_data
                        )
                    except Exception as e:
                        self.logger.error(f"Error in message handler for {channel_name}: {e}")
            
        except Exception as e:
            self.logger.error(f"Error processing incoming message: {e}")
    
    async def _qos_monitor_loop(self) -> None:
        """Monitor Quality of Service metrics."""
        while self.is_running:
            try:
                # Calculate overall average latency
                total_latency = 0
                channel_count = 0
                
                for channel_stats in self.qos_metrics["channel_stats"].values():
                    if channel_stats["average_latency_ms"] > 0:
                        total_latency += channel_stats["average_latency_ms"]
                        channel_count += 1
                
                if channel_count > 0:
                    self.qos_metrics["average_latency_ms"] = total_latency / channel_count
                
                # Log QoS metrics every 30 seconds
                self.logger.info(f"QoS Metrics: {self.qos_metrics}")
                
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error in QoS monitor: {e}")
                await asyncio.sleep(30)
    
    async def _message_cleanup_loop(self) -> None:
        """Clean up expired messages and maintain queue sizes."""
        while self.is_running:
            try:
                # Clean up expired messages for each channel
                for channel_type, config in self.channel_configs.items():
                    if config.qos_enabled:
                        await self._cleanup_channel_messages(channel_type, config)
                
                await asyncio.sleep(10)  # Cleanup every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in message cleanup: {e}")
                await asyncio.sleep(10)
    
    async def _cleanup_channel_messages(self, channel_type: ChannelType, 
                                       config: ChannelConfig) -> None:
        """Clean up expired messages for a specific channel."""
        try:
            # Get channel queue size
            queue_key = f"queue:{config.name}"
            queue_size = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.llen, queue_key
            )
            
            # Update metrics
            if channel_type.value in self.qos_metrics["channel_stats"]:
                self.qos_metrics["channel_stats"][channel_type.value]["queue_size"] = queue_size
            
            # Clean up if queue is too large
            if queue_size > config.max_queue_size:
                excess_messages = queue_size - config.max_queue_size
                await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.ltrim, queue_key, excess_messages, -1
                )
                self.logger.warning(f"Trimmed {excess_messages} messages from {config.name}")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up channel {channel_type.value}: {e}")
    
    async def _channel_health_monitor(self) -> None:
        """Monitor channel health and performance."""
        while self.is_running:
            try:
                # Check Redis connection health
                await asyncio.get_event_loop().run_in_executor(None, self.redis_client.ping)
                
                # Check for problematic channels
                for channel_name, stats in self.qos_metrics["channel_stats"].items():
                    # Alert on high latency
                    if stats["average_latency_ms"] > 1000:  # 1 second
                        self.logger.warning(f"High latency on {channel_name}: {stats['average_latency_ms']:.2f}ms")
                    
                    # Alert on high drop rate
                    total_messages = stats["messages_sent"] + stats["messages_received"]
                    if total_messages > 0:
                        drop_rate = stats["dropped_messages"] / total_messages
                        if drop_rate > 0.1:  # 10% drop rate
                            self.logger.warning(f"High drop rate on {channel_name}: {drop_rate:.1%}")
                
                await asyncio.sleep(60)  # Health check every minute
                
            except Exception as e:
                self.logger.error(f"Error in channel health monitor: {e}")
                await asyncio.sleep(60)
    
    def get_channel_stats(self) -> Dict[str, Any]:
        """Get current channel statistics."""
        return self.qos_metrics.copy()
    
    def get_channel_for_message_type(self, message_type: MessageType) -> ChannelType:
        """Get appropriate channel for message type."""
        # Map message types to channels
        channel_mapping = {
            # HFT Messages
            MessageType.HFT_ARBITRAGE_SIGNAL: ChannelType.HFT_SIGNALS,
            MessageType.HFT_MARKET_MAKING_SIGNAL: ChannelType.HFT_SIGNALS,
            MessageType.HFT_RISK_ALERT: ChannelType.HFT_SIGNALS,
            
            # Fast Execution Messages  
            MessageType.FAST_STRATEGY_SIGNAL: ChannelType.FAST_SIGNALS,
            MessageType.FAST_RISK_VALIDATION: ChannelType.FAST_SIGNALS,
            MessageType.FAST_EXECUTION_ORDER: ChannelType.FAST_SIGNALS,
            
            # Tactical Messages
            MessageType.MARKET_ANOMALY_ALERT: ChannelType.MARKET_ANOMALIES,
            MessageType.SUPPLY_DEMAND_IMBALANCE: ChannelType.TACTICAL_SIGNALS,
            MessageType.INTELLIGENCE_ANALYSIS: ChannelType.TACTICAL_SIGNALS,
            MessageType.NEWS_DRIVEN_SIGNAL: ChannelType.TACTICAL_SIGNALS,
            
            # Strategic Messages
            MessageType.STRATEGY_OPTIMIZATION: ChannelType.STRATEGIC_SIGNALS,
            MessageType.PERFORMANCE_UPDATE: ChannelType.STRATEGIC_SIGNALS,
            MessageType.REGIME_CHANGE_WARNING: ChannelType.STRATEGIC_SIGNALS,
            MessageType.LEARNING_COORDINATION: ChannelType.STRATEGIC_SIGNALS,
            
            # System Messages
            MessageType.SYSTEM_HEALTH: ChannelType.SYSTEM_HEALTH,
            MessageType.AGENT_STATUS: ChannelType.AGENT_STATUS,
            MessageType.ERROR_ALERT: ChannelType.ERROR_ALERTS
        }
        
        return channel_mapping.get(message_type, ChannelType.TACTICAL_SIGNALS)


