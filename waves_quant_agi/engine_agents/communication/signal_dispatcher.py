#!/usr/bin/env python3
"""
Signal Dispatcher
Routes and transforms signals from intelligence agent to execution queues.
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional
from .redis_channel_manager import ChannelType, ChannelConfig
from ..data_feeds.derived_signals.signal_transformer import SignalTransformer

class SignalDispatcher:
    """Dispatch signals to appropriate execution queues."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.signal_transformer = SignalTransformer(config)
        self.is_running = False
        
        # Signal routing configuration
        self.signal_routing = {
            "hft_signals": {
                "queue": "hft_signals",
                "priority": 1,
                "max_age_ms": 100,  # 100ms max age for HFT
                "batch_size": 1
            },
            "fast_signals": {
                "queue": "fast_signals", 
                "priority": 2,
                "max_age_ms": 1000,  # 1s max age for fast
                "batch_size": 5
            },
            "tactical_signals": {
                "queue": "tactical_signals",
                "priority": 3,
                "max_age_ms": 10000,  # 10s max age for tactical
                "batch_size": 10
            },
            "live_trading_signals": {
                "queue": "live_trading_signals",
                "priority": 3,
                "max_age_ms": 5000,  # 5s max age for live trading
                "batch_size": 20
            }
        }
        
        # Signal type mapping
        self.signal_type_mapping = {
            "pattern_detected": "fast_signals",
            "signal_generated": "live_trading_signals",
            "intelligence_insight": "tactical_signals",
            "market_anomaly": "fast_signals"
        }

    async def start(self):
        """Start the signal dispatcher."""
        self.is_running = True
        print("🚀 Signal Dispatcher started")
        
        # Start signal routing loop
        asyncio.create_task(self._signal_routing_loop())

    async def stop(self):
        """Stop the signal dispatcher."""
        self.is_running = False
        print("🛑 Signal Dispatcher stopped")

    async def _signal_routing_loop(self):
        """Main signal routing loop."""
        while self.is_running:
            try:
                # Process signals from intelligence agent
                await self._process_intelligence_signals()
                
                # Process signals from strategy engine
                await self._process_strategy_signals()
                
                # Process signals from market conditions
                await self._process_market_condition_signals()
                
                await asyncio.sleep(0.1)  # 100ms intervals
                
            except Exception as e:
                print(f"❌ Error in signal routing loop: {e}")
                await asyncio.sleep(1.0)

    async def _process_intelligence_signals(self):
        """Process signals from intelligence agent."""
        try:
            # Check for pattern alerts
            pattern_alerts = await self._get_redis_list("intelligence:pattern_alerts", 10)
            for alert in pattern_alerts:
                await self._route_intelligence_signal(alert, "pattern_detected")
            
            # Check for signal alerts
            signal_alerts = await self._get_redis_list("intelligence:signal_alerts", 10)
            for alert in signal_alerts:
                await self._route_intelligence_signal(alert, "signal_generated")
            
            # Check for intelligence insights
            insight_alerts = await self._get_redis_list("intelligence:insight_alerts", 10)
            for alert in insight_alerts:
                await self._route_intelligence_signal(alert, "intelligence_insight")
                
        except Exception as e:
            print(f"❌ Error processing intelligence signals: {e}")

    async def _process_strategy_signals(self):
        """Process signals from strategy engine."""
        try:
            # Check for strategy alerts
            strategy_alerts = await self._get_redis_list("strategy_engine:strategy_alerts", 10)
            for alert in strategy_alerts:
                await self._route_strategy_signal(alert)
                
        except Exception as e:
            print(f"❌ Error processing strategy signals: {e}")

    async def _process_market_condition_signals(self):
        """Process signals from market conditions agent."""
        try:
            # Check for market anomaly alerts
            anomaly_alerts = await self._get_redis_list("market_conditions:anomaly_alerts", 10)
            for alert in anomaly_alerts:
                await self._route_market_condition_signal(alert)
                
        except Exception as e:
            print(f"❌ Error processing market condition signals: {e}")

    async def _route_intelligence_signal(self, alert_data: str, alert_type: str):
        """Route intelligence signal to appropriate queue."""
        try:
            alert = json.loads(alert_data)
            signal_data = alert.get("signal_data", {})
            
            # Determine target queue based on alert type
            target_queue = self.signal_type_mapping.get(alert_type, "live_trading_signals")
            
            # Transform signal to execution-ready format
            transformed_signal = self.signal_transformer.transform_signal(signal_data, target_queue)
            
            if transformed_signal:
                # Route to appropriate queue
                await self._route_signal_to_queue(transformed_signal, target_queue)
                
                # Remove processed alert
                await self._remove_redis_list_item("intelligence:pattern_alerts", alert_data)
                
        except Exception as e:
            print(f"❌ Error routing intelligence signal: {e}")

    async def _route_strategy_signal(self, alert_data: str):
        """Route strategy signal to appropriate queue."""
        try:
            alert = json.loads(alert_data)
            signal_data = alert.get("signal_data", {})
            
            # Strategy signals go to live trading queue
            target_queue = "live_trading_signals"
            
            # Transform signal to execution-ready format
            transformed_signal = self.signal_transformer.transform_signal(signal_data, target_queue)
            
            if transformed_signal:
                # Route to appropriate queue
                await self._route_signal_to_queue(transformed_signal, target_queue)
                
                # Remove processed alert
                await self._remove_redis_list_item("strategy_engine:strategy_alerts", alert_data)
                
        except Exception as e:
            print(f"❌ Error routing strategy signal: {e}")

    async def _route_market_condition_signal(self, alert_data: str):
        """Route market condition signal to appropriate queue."""
        try:
            alert = json.loads(alert_data)
            signal_data = alert.get("signal_data", {})
            
            # Market condition signals go to fast queue
            target_queue = "fast_signals"
            
            # Transform signal to execution-ready format
            transformed_signal = self.signal_transformer.transform_signal(signal_data, target_queue)
            
            if transformed_signal:
                # Route to appropriate queue
                await self._route_signal_to_queue(transformed_signal, target_queue)
                
                # Remove processed alert
                await self._remove_redis_list_item("market_conditions:anomaly_alerts", alert_data)
                
        except Exception as e:
            print(f"❌ Error routing market condition signal: {e}")

    async def _route_signal_to_queue(self, signal: Dict[str, Any], queue_name: str):
        """Route a transformed signal to the specified queue."""
        try:
            # Get queue configuration
            queue_config = self.signal_routing.get(queue_name, {})
            
            # Validate signal age
            signal_age_ms = (time.time() - signal.get("timestamp", 0)) * 1000
            max_age_ms = queue_config.get("max_age_ms", 5000)
            
            if signal_age_ms > max_age_ms:
                print(f"⚠️ Signal too old for {queue_name}: {signal_age_ms:.1f}ms > {max_age_ms}ms")
                return
            
            # Add signal to queue
            await self._add_to_redis_queue(queue_name, signal)
            
            print(f"✅ Signal routed to {queue_name}: {signal.get('symbol', 'Unknown')} - {signal.get('action', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error routing signal to queue {queue_name}: {e}")

    async def _get_redis_list(self, key: str, max_items: int) -> List[str]:
        """Get items from Redis list (placeholder - should use actual Redis connection)."""
        # This is a placeholder - in production, use actual Redis connection
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            return r.lrange(key, 0, max_items - 1)
        except:
            return []

    async def _add_to_redis_queue(self, queue_name: str, signal: Dict[str, Any]):
        """Add signal to Redis queue (placeholder - should use actual Redis connection)."""
        # This is a placeholder - in production, use actual Redis connection
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            r.lpush(queue_name, json.dumps(signal))
        except Exception as e:
            print(f"❌ Error adding to Redis queue {queue_name}: {e}")

    async def _remove_redis_list_item(self, key: str, item: str):
        """Remove item from Redis list (placeholder - should use actual Redis connection)."""
        # This is a placeholder - in production, use actual Redis connection
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            r.lrem(key, 0, item)
        except Exception as e:
            print(f"❌ Error removing item from Redis list {key}: {e}")

    async def get_dispatch_status(self) -> Dict[str, Any]:
        """Get current dispatch status."""
        return {
            "is_running": self.is_running,
            "signal_routing": self.signal_routing,
            "signal_type_mapping": self.signal_type_mapping,
            "last_update": time.time()
        }
