# failure_prevention/__init__.py
"""
Failure Prevention Agent - Autonomous Trading System Guardian
=============================================================

A self-contained, scalable failure prevention system that monitors,
protects, and learns from both internal system behavior and external
intelligence sources to prevent trading system failures.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime, timedelta

__version__ = "1.0.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class AlertLevel(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class FailureType(Enum):
    """Types of failures the system can detect"""
    SYSTEM_LAG = "system_lag"
    MEMORY_LEAK = "memory_leak"
    AGENT_FAILURE = "agent_failure"
    DATA_CORRUPTION = "data_corruption"
    NETWORK_ISSUE = "network_issue"
    BROKER_DISCONNECT = "broker_disconnect"
    STRATEGY_LOOP = "strategy_loop"
    EXTERNAL_THREAT = "external_threat"

@dataclass
class FailureEvent:
    """Represents a detected failure event"""
    timestamp: datetime
    failure_type: FailureType
    alert_level: AlertLevel
    source: str
    description: str
    metadata: Dict[str, Any]
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None

class FailurePreventionAgent:
    """
    Main orchestrator for the failure prevention system.
    Coordinates all monitoring, circuit breaking, learning, and recovery operations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        self.components = {}
        self.event_queue = asyncio.Queue()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize all subsystems
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all subsystem components"""
        from .monitor.system_watcher import SystemWatcher
        from .monitor.agent_supervisor import AgentSupervisor
        from .monitor.data_integrity_checker import DataIntegrityChecker
        from .circuit_breakers.broker_breaker import BrokerBreaker
        from .circuit_breakers.strategy_breaker import StrategyBreaker
        from .circuit_breakers.trade_halt_switch import TradeHaltSwitch
        from .redundancy.fallback_manager import FallbackManager
        from .infrastructure.network_guard import NetworkGuard
        from .learning_layer.external.intelligence_fusion.pattern_synthesizer import PatternSynthesizer
        
        self.components = {
            'system_watcher': SystemWatcher(self.config.get('system', {})),
            'agent_supervisor': AgentSupervisor(self.config.get('agents', {})),
            'data_checker': DataIntegrityChecker(self.config.get('data', {})),
            'broker_breaker': BrokerBreaker(self.config.get('brokers', {})),
            'strategy_breaker': StrategyBreaker(self.config.get('strategies', {})),
            'trade_halt': TradeHaltSwitch(self.config.get('trading', {})),
            'fallback_manager': FallbackManager(self.config.get('redundancy', {})),
            'network_guard': NetworkGuard(self.config.get('network', {})),
            'pattern_synthesizer': PatternSynthesizer(self.config.get('learning', {}))
        }
    
    async def start(self):
        """Start the failure prevention agent"""
        self.logger.info("Starting Failure Prevention Agent...")
        self.is_running = True
        
        # Start all monitoring components
        tasks = []
        for name, component in self.components.items():
            if hasattr(component, 'start'):
                task = asyncio.create_task(component.start())
                tasks.append(task)
                self.logger.info(f"Started {name}")
        
        # Start main event processing loop
        tasks.append(asyncio.create_task(self._process_events()))
        
        # Start learning and intelligence gathering
        tasks.append(asyncio.create_task(self._intelligence_loop()))
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            await self.stop()
    
    async def stop(self):
        """Gracefully stop the failure prevention agent"""
        self.logger.info("Stopping Failure Prevention Agent...")
        self.is_running = False
        
        # Stop all components
        for name, component in self.components.items():
            if hasattr(component, 'stop'):
                await component.stop()
                self.logger.info(f"Stopped {name}")
    
    async def _process_events(self):
        """Main event processing loop"""
        while self.is_running:
            try:
                # Process events from the queue
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                await self._handle_failure_event(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
    
    async def _handle_failure_event(self, event: FailureEvent):
        """Handle a detected failure event"""
        self.logger.warning(f"Processing failure event: {event.failure_type.value} - {event.description}")
        
        # Trigger appropriate circuit breakers
        if event.failure_type == FailureType.BROKER_DISCONNECT:
            await self.components['broker_breaker'].activate(event.source)
        elif event.failure_type == FailureType.STRATEGY_LOOP:
            await self.components['strategy_breaker'].activate(event.source)
        elif event.alert_level == AlertLevel.CRITICAL:
            await self.components['trade_halt'].emergency_stop()
        
        # Activate fallback systems if needed
        if event.alert_level in [AlertLevel.HIGH, AlertLevel.CRITICAL]:
            await self.components['fallback_manager'].activate_fallback(event.failure_type)
        
        # Log for learning
        await self._log_for_learning(event)
    
    async def _intelligence_loop(self):
        """Continuous external intelligence gathering and analysis"""
        while self.is_running:
            try:
                # Gather external intelligence
                await self.components['pattern_synthesizer'].gather_external_intelligence()
                
                # Sleep for intelligence gathering interval
                await asyncio.sleep(self.config.get('intelligence_interval', 300))  # 5 minutes default
            except Exception as e:
                self.logger.error(f"Error in intelligence loop: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute
    
    async def _log_for_learning(self, event: FailureEvent):
        """Log event for machine learning purposes"""
        try:
            from .memory.incident_cache import IncidentCache
            cache = IncidentCache()
            await cache.store_incident(event)
        except Exception as e:
            self.logger.error(f"Error logging for learning: {e}")
    
    async def report_event(self, failure_type: FailureType, alert_level: AlertLevel, 
                          source: str, description: str, metadata: Dict[str, Any] = None):
        """Public interface for reporting failure events"""
        event = FailureEvent(
            timestamp=datetime.now(),
            failure_type=failure_type,
            alert_level=alert_level,
            source=source,
            description=description,
            metadata=metadata or {}
        )
        await self.event_queue.put(event)