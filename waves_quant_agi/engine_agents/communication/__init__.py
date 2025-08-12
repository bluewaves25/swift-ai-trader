#!/usr/bin/env python3
"""
Communication Package for 4-Tier Trading Engine
Standardized message formats and intelligent routing system
"""

from .message_formats import (
    MessageType,
    MessagePriority,
    MessageFormat,
    HFTArbitrageSignal,
    HFTMarketMakingSignal,
    FastStrategySignal,
    FastRiskValidation,
    MarketAnomalyAlert,
    SupplyDemandImbalance,
    IntelligenceAnalysis,
    StrategyOptimization,
    PerformanceUpdate,
    RegimeChangeWarning,
    SystemHealthAlert,
    AgentStatusUpdate,
    create_hft_arbitrage_signal,
    create_market_anomaly_alert,
    create_strategy_signal,
    create_market_data_update,
    create_agent_heartbeat,
    validate_message_format,
    validate_hft_timing,
    get_channel_for_message
)

from .redis_channel_manager import (
    RedisChannelManager,
    ChannelType,
    ChannelConfig
)

from .communication_hub import (
    CommunicationHub
)

__all__ = [
    # Message Types and Priorities
    'MessageType',
    'MessagePriority',
    
    # Base Message Format
    'MessageFormat',
    
    # HFT Message Formats
    'HFTArbitrageSignal',
    'HFTMarketMakingSignal',
    
    # Fast Execution Message Formats
    'FastStrategySignal',
    'FastRiskValidation',
    
    # Tactical Message Formats
    'MarketAnomalyAlert',
    'SupplyDemandImbalance',
    'IntelligenceAnalysis',
    
    # Strategic Message Formats
    'StrategyOptimization',
    'PerformanceUpdate',
    'RegimeChangeWarning',
    
    # System Message Formats
    'SystemHealthAlert',
    'AgentStatusUpdate',
    
    # Factory Functions
    'create_hft_arbitrage_signal',
    'create_market_anomaly_alert',
    'create_strategy_signal',
    'create_market_data_update',
    'create_agent_heartbeat',
    
    # Validation Functions
    'validate_message_format',
    'validate_hft_timing',
    'get_channel_for_message',
    
    # Channel Management
    'RedisChannelManager',
    'ChannelType',
    'ChannelConfig',
    
    # Communication Hub
    'CommunicationHub'
]

# Package version
__version__ = "1.0.0"

# Package description
__description__ = "Standardized communication system for 4-tier trading engine"
