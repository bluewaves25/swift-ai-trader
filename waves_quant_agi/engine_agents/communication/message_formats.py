#!/usr/bin/env python3
"""
Standardized Message Formats for 4-Tier Trading Engine
Eliminates communication misinterpretations between agents
"""

from typing import Dict, Any, List, Optional
from enum import Enum
import time
import json

class MessageType(Enum):
    """Standardized message types for all agent communication."""
    
    # TIER 1: Ultra-HFT Messages (1ms-10ms)
    HFT_ARBITRAGE_SIGNAL = "hft_arbitrage_signal"
    HFT_MARKET_MAKING_SIGNAL = "hft_market_making_signal"
    HFT_RISK_ALERT = "hft_risk_alert"
    
    # TIER 2: Fast Execution Messages (100ms-1s)
    FAST_STRATEGY_SIGNAL = "fast_strategy_signal"
    FAST_RISK_VALIDATION = "fast_risk_validation"
    FAST_EXECUTION_ORDER = "fast_execution_order"
    MARKET_DATA_UPDATE = "market_data_update"
    
    # TIER 3: Tactical Messages (1s-60s)
    MARKET_ANOMALY_ALERT = "market_anomaly_alert"
    SUPPLY_DEMAND_IMBALANCE = "supply_demand_imbalance"
    INTELLIGENCE_ANALYSIS = "intelligence_analysis"
    NEWS_DRIVEN_SIGNAL = "news_driven_signal"
    
    # TIER 4: Strategic Messages (1min-1hour)
    STRATEGY_OPTIMIZATION = "strategy_optimization"
    PERFORMANCE_UPDATE = "performance_update"
    REGIME_CHANGE_WARNING = "regime_change_warning"
    LEARNING_COORDINATION = "learning_coordination"
    
    # Cross-Tier Messages
    SYSTEM_HEALTH = "system_health"
    AGENT_STATUS = "agent_status"
    ERROR_ALERT = "error_alert"

class MessagePriority(Enum):
    """Message priority levels for routing."""
    CRITICAL = 1    # Ultra-HFT execution signals
    HIGH = 2        # Fast execution signals
    MEDIUM = 3      # Tactical analysis
    LOW = 4         # Strategic coordination

class MessageFormat:
    """Base class for all standardized messages."""
    
    def __init__(self, message_type: MessageType, source_agent: str, priority: MessagePriority = MessagePriority.MEDIUM):
        self.message_type = message_type
        self.source_agent = source_agent
        self.priority = priority
        self.timestamp = time.time()
        self.message_id = self._generate_message_id()
    
    def _generate_message_id(self) -> str:
        """Generate unique message ID."""
        return f"{self.source_agent}_{self.message_type.value}_{int(self.timestamp * 1000000)}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for Redis transmission."""
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "source_agent": self.source_agent,
            "priority": self.priority.value,
            "timestamp": self.timestamp
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string for Redis transmission."""
        return json.dumps(self.to_dict())

# TIER 1: Ultra-HFT Message Formats

class HFTArbitrageSignal(MessageFormat):
    """Ultra-fast arbitrage opportunity signal."""
    
    def __init__(self, source_agent: str, symbol: str, exchange1: str, exchange2: str, 
                 price_diff: float, max_latency_ms: int, expires_at_ms: float):
        super().__init__(MessageType.HFT_ARBITRAGE_SIGNAL, source_agent, MessagePriority.CRITICAL)
        self.symbol = symbol
        self.exchange1 = exchange1
        self.exchange2 = exchange2
        self.price_diff = price_diff
        self.max_latency_ms = max_latency_ms
        self.expires_at_ms = expires_at_ms
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "symbol": self.symbol,
            "exchange1": self.exchange1,
            "exchange2": self.exchange2,
            "price_diff": self.price_diff,
            "max_latency_ms": self.max_latency_ms,
            "expires_at_ms": self.expires_at_ms,
            "execution_priority": 1
        })
        return base

class HFTMarketMakingSignal(MessageFormat):
    """Ultra-fast market making signal."""
    
    def __init__(self, source_agent: str, symbol: str, bid_price: float, ask_price: float,
                 bid_size: float, ask_size: float, spread: float, inventory_level: float):
        super().__init__(MessageType.HFT_MARKET_MAKING_SIGNAL, source_agent, MessagePriority.CRITICAL)
        self.symbol = symbol
        self.bid_price = bid_price
        self.ask_price = ask_price
        self.bid_size = bid_size
        self.ask_size = ask_size
        self.spread = spread
        self.inventory_level = inventory_level
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "symbol": self.symbol,
            "bid_price": self.bid_price,
            "ask_price": self.ask_price,
            "bid_size": self.bid_size,
            "ask_size": self.ask_size,
            "spread": self.spread,
            "inventory_level": self.inventory_level,
            "execution_priority": 1
        })
        return base

# TIER 2: Fast Execution Message Formats

class FastStrategySignal(MessageFormat):
    """Fast strategy execution signal."""
    
    def __init__(self, source_agent: str, strategy_type: str, strategy_subtype: str,
                 symbol: str, action: str, confidence: float, entry_price: Optional[float] = None,
                 stop_loss: Optional[float] = None, take_profit: Optional[float] = None):
        super().__init__(MessageType.FAST_STRATEGY_SIGNAL, source_agent, MessagePriority.HIGH)
        self.strategy_type = strategy_type
        self.strategy_subtype = strategy_subtype
        self.symbol = symbol
        self.action = action  # buy, sell, hold
        self.confidence = confidence
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "strategy_type": self.strategy_type,
            "strategy_subtype": self.strategy_subtype,
            "symbol": self.symbol,
            "action": self.action,
            "confidence": self.confidence,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "execution_priority": 2
        })
        return base

class FastRiskValidation(MessageFormat):
    """Fast risk validation message."""
    
    def __init__(self, source_agent: str, validation_result: bool, risk_score: float,
                 position_size_allowed: float, warnings: List[str]):
        super().__init__(MessageType.FAST_RISK_VALIDATION, source_agent, MessagePriority.HIGH)
        self.validation_result = validation_result
        self.risk_score = risk_score
        self.position_size_allowed = position_size_allowed
        self.warnings = warnings
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "validation_result": self.validation_result,
            "risk_score": self.risk_score,
            "position_size_allowed": self.position_size_allowed,
            "warnings": self.warnings,
            "execution_priority": 2
        })
        return base

# TIER 3: Tactical Message Formats

class MarketAnomalyAlert(MessageFormat):
    """Market anomaly alert from Market Conditions Agent."""
    
    def __init__(self, source_agent: str, anomaly_type: str, severity: str,
                 affected_assets: List[str], confidence: float, time_to_impact: int,
                 recommended_actions: List[str]):
        super().__init__(MessageType.MARKET_ANOMALY_ALERT, source_agent, MessagePriority.HIGH)
        self.anomaly_type = anomaly_type
        self.severity = severity  # critical, high, medium
        self.affected_assets = affected_assets
        self.confidence = confidence
        self.time_to_impact = time_to_impact  # seconds
        self.recommended_actions = recommended_actions
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "affected_assets": self.affected_assets,
            "confidence": self.confidence,
            "time_to_impact": self.time_to_impact,
            "recommended_actions": self.recommended_actions,
            "early_warning": True
        })
        return base

class SupplyDemandImbalance(MessageFormat):
    """Supply/demand imbalance alert."""
    
    def __init__(self, source_agent: str, symbol: str, imbalance_type: str,
                 magnitude: float, order_flow_data: Dict[str, Any]):
        super().__init__(MessageType.SUPPLY_DEMAND_IMBALANCE, source_agent, MessagePriority.MEDIUM)
        self.symbol = symbol
        self.imbalance_type = imbalance_type  # supply_shortage, demand_surge, etc.
        self.magnitude = magnitude
        self.order_flow_data = order_flow_data
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "symbol": self.symbol,
            "imbalance_type": self.imbalance_type,
            "magnitude": self.magnitude,
            "order_flow_data": self.order_flow_data
        })
        return base

class IntelligenceAnalysis(MessageFormat):
    """Intelligence analysis from Intelligence Agent."""
    
    def __init__(self, source_agent: str, analysis_type: str, strategy_context: str,
                 insights: Dict[str, Any], confidence: float, validity_duration: int):
        super().__init__(MessageType.INTELLIGENCE_ANALYSIS, source_agent, MessagePriority.MEDIUM)
        self.analysis_type = analysis_type
        self.strategy_context = strategy_context
        self.insights = insights
        self.confidence = confidence
        self.validity_duration = validity_duration  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "analysis_type": self.analysis_type,
            "strategy_context": self.strategy_context,
            "insights": self.insights,
            "confidence": self.confidence,
            "validity_duration": self.validity_duration
        })
        return base

# TIER 4: Strategic Message Formats

class StrategyOptimization(MessageFormat):
    """Strategy optimization update."""
    
    def __init__(self, source_agent: str, strategy_type: str, optimization_type: str,
                 parameter_adjustments: Dict[str, Any], performance_improvement: float):
        super().__init__(MessageType.STRATEGY_OPTIMIZATION, source_agent, MessagePriority.LOW)
        self.strategy_type = strategy_type
        self.optimization_type = optimization_type
        self.parameter_adjustments = parameter_adjustments
        self.performance_improvement = performance_improvement
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "strategy_type": self.strategy_type,
            "optimization_type": self.optimization_type,
            "parameter_adjustments": self.parameter_adjustments,
            "performance_improvement": self.performance_improvement
        })
        return base

class PerformanceUpdate(MessageFormat):
    """Performance tracking update."""
    
    def __init__(self, source_agent: str, component: str, metrics: Dict[str, Any],
                 performance_grade: str, recommendations: List[str]):
        super().__init__(MessageType.PERFORMANCE_UPDATE, source_agent, MessagePriority.LOW)
        self.component = component
        self.metrics = metrics
        self.performance_grade = performance_grade  # excellent, good, poor
        self.recommendations = recommendations
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "component": self.component,
            "metrics": self.metrics,
            "performance_grade": self.performance_grade,
            "recommendations": self.recommendations
        })
        return base

class RegimeChangeWarning(MessageFormat):
    """Market regime change warning."""
    
    def __init__(self, source_agent: str, current_regime: str, predicted_regime: str,
                 confidence: float, time_to_change: int, preparation_actions: List[str]):
        super().__init__(MessageType.REGIME_CHANGE_WARNING, source_agent, MessagePriority.MEDIUM)
        self.current_regime = current_regime
        self.predicted_regime = predicted_regime
        self.confidence = confidence
        self.time_to_change = time_to_change  # seconds
        self.preparation_actions = preparation_actions
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "current_regime": self.current_regime,
            "predicted_regime": self.predicted_regime,
            "confidence": self.confidence,
            "time_to_change": self.time_to_change,
            "preparation_actions": self.preparation_actions
        })
        return base

# Cross-Tier Message Formats

class SystemHealthAlert(MessageFormat):
    """System health alert."""
    
    def __init__(self, source_agent: str, health_status: str, affected_components: List[str],
                 severity: str, recovery_actions: List[str]):
        super().__init__(MessageType.SYSTEM_HEALTH, source_agent, MessagePriority.HIGH)
        self.health_status = health_status
        self.affected_components = affected_components
        self.severity = severity
        self.recovery_actions = recovery_actions
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "health_status": self.health_status,
            "affected_components": self.affected_components,
            "severity": self.severity,
            "recovery_actions": self.recovery_actions
        })
        return base

class AgentStatusUpdate(MessageFormat):
    """Agent status update."""
    
    def __init__(self, source_agent: str, status: str, uptime: float, 
                 performance_metrics: Dict[str, Any], active_tasks: List[str]):
        super().__init__(MessageType.AGENT_STATUS, source_agent, MessagePriority.LOW)
        self.status = status  # running, paused, error, stopping
        self.uptime = uptime
        self.performance_metrics = performance_metrics
        self.active_tasks = active_tasks
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "status": self.status,
            "uptime": self.uptime,
            "performance_metrics": self.performance_metrics,
            "active_tasks": self.active_tasks
        })
        return base

# Message Factory Functions

def create_hft_arbitrage_signal(source: str, symbol: str, exchange1: str, exchange2: str, 
                               price_diff: float, max_latency: int, expires_at: float) -> HFTArbitrageSignal:
    """Factory function for HFT arbitrage signals."""
    return HFTArbitrageSignal(source, symbol, exchange1, exchange2, price_diff, max_latency, expires_at)

def create_market_anomaly_alert(source: str, anomaly_type: str, severity: str,
                               affected_assets: List[str], confidence: float, 
                               time_to_impact: int, actions: List[str]) -> MarketAnomalyAlert:
    """Factory function for market anomaly alerts."""
    return MarketAnomalyAlert(source, anomaly_type, severity, affected_assets, 
                             confidence, time_to_impact, actions)

def create_strategy_signal(source: str, strategy_type: str, subtype: str, symbol: str,
                          action: str, confidence: float, entry: float = None,
                          stop: float = None, target: float = None) -> FastStrategySignal:
    """Factory function for strategy signals."""
    return FastStrategySignal(source, strategy_type, subtype, symbol, action, 
                             confidence, entry, stop, target)

def create_market_data_update(source: str, symbol: str, price: float, 
                             volume: float, timestamp: float) -> Dict[str, Any]:
    """Create a market data update message."""
    return {
        "message_id": f"{source}_{symbol}_{int(timestamp)}",
        "message_type": MessageType.MARKET_DATA_UPDATE.value,
        "source_agent": source,
        "priority": MessagePriority.HIGH.value,
        "timestamp": timestamp,
        "content": {
            "symbol": symbol,
            "price": price,
            "volume": volume
        }
    }

def create_agent_heartbeat(source: str, status: str, timestamp: float) -> Dict[str, Any]:
    """Create an agent heartbeat message."""
    return {
        "message_id": f"{source}_heartbeat_{int(timestamp)}",
        "message_type": MessageType.AGENT_STATUS_UPDATE.value,
        "source_agent": source,
        "priority": MessagePriority.LOW.value,
        "timestamp": timestamp,
        "content": {
            "status": status,
            "heartbeat": True
        }
    }

# Message Validation Functions

def validate_message_format(message_dict: Dict[str, Any]) -> bool:
    """Validate message format compliance."""
    required_fields = ["message_id", "message_type", "source_agent", "priority", "timestamp"]
    return all(field in message_dict for field in required_fields)

def validate_hft_timing(message: MessageFormat) -> bool:
    """Validate HFT message timing requirements."""
    if message.priority == MessagePriority.CRITICAL:
        # HFT messages must be processed within 10ms
        age_ms = (time.time() - message.timestamp) * 1000
        return age_ms <= 10
    return True

def get_channel_for_message(message: MessageFormat) -> str:
    """Get appropriate Redis channel for message."""
    channel_mapping = {
        MessagePriority.CRITICAL: "hft_signals",      # Ultra-HFT
        MessagePriority.HIGH: "fast_signals",         # Fast execution
        MessagePriority.MEDIUM: "tactical_signals",   # Tactical analysis
        MessagePriority.LOW: "strategic_signals"      # Strategic coordination
    }
    return channel_mapping.get(message.priority, "general_signals")


