#!/usr/bin/env python3
"""
Agent Integration Example for Communication System
Shows how to integrate existing agents with the new standardized communication
"""

import asyncio
import time
from typing import Dict, Any
from communication import (
    CommunicationHub, 
    ChannelType, 
    MessageType,
    create_market_anomaly_alert,
    create_strategy_signal,
    FastRiskValidation,
    MarketAnomalyAlert
)

class EnhancedAgentBase:
    """Base class for agents with standardized communication."""
    
    def __init__(self, agent_id: str, agent_type: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.config = config
        self.is_running = False
        
        # Communication hub
        self.comm_hub = None
        
        # Define which channels this agent subscribes to
        self.subscribed_channels = self._get_subscribed_channels()
        
        # Define message handlers
        self.message_handlers = self._get_message_handlers()
    
    def _get_subscribed_channels(self) -> list:
        """Override in child classes to specify channels."""
        return []
    
    def _get_message_handlers(self) -> Dict[MessageType, callable]:
        """Override in child classes to specify message handlers."""
        return {}
    
    async def initialize_communication(self, comm_hub: CommunicationHub) -> bool:
        """Initialize communication with the hub."""
        try:
            self.comm_hub = comm_hub
            
            # Register with communication hub
            success = await self.comm_hub.register_agent(
                self.agent_id,
                self.agent_type,
                self.subscribed_channels,
                self.message_handlers
            )
            
            if success:
                print(f"[{self.agent_id}] Successfully registered with communication hub")
                return True
            else:
                print(f"[{self.agent_id}] Failed to register with communication hub")
                return False
                
        except Exception as e:
            print(f"[{self.agent_id}] Error initializing communication: {e}")
            return False
    
    async def send_message(self, message) -> bool:
        """Send message through communication hub."""
        if self.comm_hub:
            return await self.comm_hub.send_message(message)
        return False
    
    async def send_heartbeat(self) -> None:
        """Send heartbeat to communication hub."""
        if self.comm_hub:
            await self.comm_hub.update_agent_heartbeat(self.agent_id)
    
    async def start_heartbeat_loop(self) -> None:
        """Start heartbeat loop."""
        while self.is_running:
            await self.send_heartbeat()
            await asyncio.sleep(30)  # Heartbeat every 30 seconds

class EnhancedStrategyEngineAgent(EnhancedAgentBase):
    """Enhanced Strategy Engine Agent with standardized communication."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("strategy_engine", "strategy", config)
    
    def _get_subscribed_channels(self) -> list:
        """Strategy Engine subscribes to market anomalies and intelligence."""
        return [
            ChannelType.MARKET_ANOMALIES,
            ChannelType.INTELLIGENCE_ALERTS,
            ChannelType.STRATEGY_ENGINE_ALERTS
        ]
    
    def _get_message_handlers(self) -> Dict[MessageType, callable]:
        """Strategy Engine message handlers."""
        return {
            MessageType.MARKET_ANOMALY_ALERT: self._handle_market_anomaly,
            MessageType.INTELLIGENCE_ANALYSIS: self._handle_intelligence,
            MessageType.FAST_RISK_VALIDATION: self._handle_risk_validation
        }
    
    def _handle_market_anomaly(self, message_data: Dict[str, Any]) -> None:
        """Handle market anomaly alerts."""
        try:
            anomaly_type = message_data.get("anomaly_type")
            severity = message_data.get("severity")
            affected_assets = message_data.get("affected_assets", [])
            recommended_actions = message_data.get("recommended_actions", [])
            
            print(f"[Strategy Engine] Market anomaly detected: {anomaly_type} ({severity})")
            print(f"[Strategy Engine] Affected assets: {affected_assets}")
            print(f"[Strategy Engine] Recommended actions: {recommended_actions}")
            
            # Implement strategy adjustments based on anomaly
            if "pause_market_making" in recommended_actions:
                self._pause_market_making_strategies()
            
            if "reduce_positions" in recommended_actions:
                self._reduce_position_sizes()
                
        except Exception as e:
            print(f"[Strategy Engine] Error handling market anomaly: {e}")
    
    def _handle_intelligence(self, message_data: Dict[str, Any]) -> None:
        """Handle intelligence analysis."""
        try:
            analysis_type = message_data.get("analysis_type")
            strategy_context = message_data.get("strategy_context")
            insights = message_data.get("insights", {})
            confidence = message_data.get("confidence", 0.0)
            
            print(f"[Strategy Engine] Intelligence received: {analysis_type} for {strategy_context}")
            print(f"[Strategy Engine] Confidence: {confidence:.2f}")
            
            # Apply intelligence to strategy selection
            if confidence > 0.8:
                self._apply_high_confidence_intelligence(insights, strategy_context)
                
        except Exception as e:
            print(f"[Strategy Engine] Error handling intelligence: {e}")
    
    def _handle_risk_validation(self, message_data: Dict[str, Any]) -> None:
        """Handle risk validation responses."""
        try:
            validation_result = message_data.get("validation_result")
            risk_score = message_data.get("risk_score", 0.0)
            position_size_allowed = message_data.get("position_size_allowed", 0.0)
            warnings = message_data.get("warnings", [])
            
            print(f"[Strategy Engine] Risk validation: {validation_result}")
            print(f"[Strategy Engine] Risk score: {risk_score:.2f}")
            print(f"[Strategy Engine] Position size allowed: {position_size_allowed}")
            
            if warnings:
                print(f"[Strategy Engine] Risk warnings: {warnings}")
                
        except Exception as e:
            print(f"[Strategy Engine] Error handling risk validation: {e}")
    
    async def send_strategy_signal(self, strategy_type: str, symbol: str, action: str, confidence: float) -> bool:
        """Send strategy signal using standardized format."""
        try:
            strategy_signal = create_strategy_signal(
                self.agent_id,
                strategy_type,
                "default",  # subtype
                symbol,
                action,
                confidence
            )
            
            success = await self.send_message(strategy_signal)
            if success:
                print(f"[Strategy Engine] Sent strategy signal: {action} {symbol} ({confidence:.2f})")
            
            return success
            
        except Exception as e:
            print(f"[Strategy Engine] Error sending strategy signal: {e}")
            return False
    
    def _pause_market_making_strategies(self) -> None:
        """Pause market making strategies."""
        print("[Strategy Engine] Pausing market making strategies")
        # Implementation here
    
    def _reduce_position_sizes(self) -> None:
        """Reduce position sizes."""
        print("[Strategy Engine] Reducing position sizes")
        # Implementation here
    
    def _apply_high_confidence_intelligence(self, insights: Dict[str, Any], context: str) -> None:
        """Apply high confidence intelligence to strategy selection."""
        print(f"[Strategy Engine] Applying high confidence intelligence for {context}")
        # Implementation here

class EnhancedMarketConditionsAgent(EnhancedAgentBase):
    """Enhanced Market Conditions Agent with standardized communication."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("market_conditions", "market_analysis", config)
    
    def _get_subscribed_channels(self) -> list:
        """Market Conditions Agent doesn't subscribe to many channels (it's mainly a sender)."""
        return [
            ChannelType.SYSTEM_HEALTH
        ]
    
    def _get_message_handlers(self) -> Dict[MessageType, callable]:
        """Market Conditions message handlers."""
        return {
            MessageType.SYSTEM_HEALTH: self._handle_system_health
        }
    
    def _handle_system_health(self, message_data: Dict[str, Any]) -> None:
        """Handle system health alerts."""
        try:
            health_status = message_data.get("health_status")
            affected_components = message_data.get("affected_components", [])
            
            print(f"[Market Conditions] System health alert: {health_status}")
            print(f"[Market Conditions] Affected components: {affected_components}")
            
        except Exception as e:
            print(f"[Market Conditions] Error handling system health: {e}")
    
    async def send_market_anomaly_alert(self, anomaly_type: str, severity: str, 
                                       affected_assets: list, confidence: float) -> bool:
        """Send market anomaly alert using standardized format."""
        try:
            anomaly_alert = create_market_anomaly_alert(
                self.agent_id,
                anomaly_type,
                severity,
                affected_assets,
                confidence,
                300,  # time_to_impact
                ["pause_market_making", "reduce_positions"]  # recommended_actions
            )
            
            success = await self.send_message(anomaly_alert)
            if success:
                print(f"[Market Conditions] Sent anomaly alert: {anomaly_type} ({severity})")
            
            return success
            
        except Exception as e:
            print(f"[Market Conditions] Error sending anomaly alert: {e}")
            return False

class EnhancedRiskManagementAgent(EnhancedAgentBase):
    """Enhanced Risk Management Agent with standardized communication."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("risk_management", "risk", config)
    
    def _get_subscribed_channels(self) -> list:
        """Risk Management subscribes to strategy signals and market anomalies."""
        return [
            ChannelType.FAST_SIGNALS,
            ChannelType.MARKET_ANOMALIES,
            ChannelType.RISK_MANAGEMENT_ALERTS
        ]
    
    def _get_message_handlers(self) -> Dict[MessageType, callable]:
        """Risk Management message handlers."""
        return {
            MessageType.FAST_STRATEGY_SIGNAL: self._handle_strategy_signal,
            MessageType.MARKET_ANOMALY_ALERT: self._handle_market_anomaly
        }
    
    def _handle_strategy_signal(self, message_data: Dict[str, Any]) -> None:
        """Handle strategy signals for risk validation."""
        try:
            strategy_type = message_data.get("strategy_type")
            symbol = message_data.get("symbol")
            action = message_data.get("action")
            confidence = message_data.get("confidence", 0.0)
            
            print(f"[Risk Management] Validating strategy: {action} {symbol}")
            
            # Perform risk validation
            risk_score = self._calculate_risk_score(strategy_type, symbol, action)
            validation_result = risk_score < 0.5  # Risk threshold
            position_size_allowed = max(0.0, 1.0 - risk_score)
            
            # Send risk validation response
            asyncio.create_task(self._send_risk_validation(
                validation_result, risk_score, position_size_allowed
            ))
            
        except Exception as e:
            print(f"[Risk Management] Error handling strategy signal: {e}")
    
    def _handle_market_anomaly(self, message_data: Dict[str, Any]) -> None:
        """Handle market anomaly alerts for risk adjustment."""
        try:
            anomaly_type = message_data.get("anomaly_type")
            severity = message_data.get("severity")
            
            print(f"[Risk Management] Adjusting risk parameters for {anomaly_type} ({severity})")
            
            # Adjust risk parameters based on anomaly
            if severity == "critical":
                self._tighten_risk_limits(0.5)  # Reduce limits by 50%
            elif severity == "high":
                self._tighten_risk_limits(0.3)  # Reduce limits by 30%
                
        except Exception as e:
            print(f"[Risk Management] Error handling market anomaly: {e}")
    
    async def _send_risk_validation(self, result: bool, risk_score: float, position_size: float) -> bool:
        """Send risk validation response."""
        try:
            risk_validation = FastRiskValidation(
                self.agent_id,
                result,
                risk_score,
                position_size,
                ["market_volatility"] if risk_score > 0.3 else []
            )
            
            success = await self.send_message(risk_validation)
            if success:
                print(f"[Risk Management] Sent risk validation: {result} (score: {risk_score:.2f})")
            
            return success
            
        except Exception as e:
            print(f"[Risk Management] Error sending risk validation: {e}")
            return False
    
    def _calculate_risk_score(self, strategy_type: str, symbol: str, action: str) -> float:
        """Calculate risk score for strategy."""
        # Simplified risk calculation
        base_risk = 0.2
        
        if strategy_type == "market_making":
            base_risk += 0.1
        elif strategy_type == "arbitrage":
            base_risk += 0.3
        
        if action == "sell":
            base_risk += 0.1
        
        return min(1.0, base_risk)
    
    def _tighten_risk_limits(self, reduction_factor: float) -> None:
        """Tighten risk limits by reduction factor."""
        print(f"[Risk Management] Tightening risk limits by {reduction_factor:.1%}")
        # Implementation here

# Integration Test Example
async def test_communication_integration():
    """Test the enhanced agent communication system."""
    print("Starting Communication Integration Test...")
    
    # Communication hub configuration
    config = {
        "redis": {
            "redis_host": "localhost",
            "redis_port": 6379,
            "redis_db": 0
        },
        "heartbeat_timeout": 60
    }
    
    # Create communication hub
    comm_hub = CommunicationHub(config)
    await comm_hub.start()
    
    # Create enhanced agents
    strategy_agent = EnhancedStrategyEngineAgent(config)
    market_agent = EnhancedMarketConditionsAgent(config)
    risk_agent = EnhancedRiskManagementAgent(config)
    
    # Initialize communication for all agents
    await strategy_agent.initialize_communication(comm_hub)
    await market_agent.initialize_communication(comm_hub)
    await risk_agent.initialize_communication(comm_hub)
    
    # Start heartbeat loops
    strategy_agent.is_running = True
    market_agent.is_running = True
    risk_agent.is_running = True
    
    asyncio.create_task(strategy_agent.start_heartbeat_loop())
    asyncio.create_task(market_agent.start_heartbeat_loop())
    asyncio.create_task(risk_agent.start_heartbeat_loop())
    
    # Test communication flow
    print("\n--- Testing Communication Flow ---")
    
    # 1. Market Conditions sends anomaly alert
    print("\n1. Market Conditions sending anomaly alert...")
    await market_agent.send_market_anomaly_alert(
        "correlation_break", 
        "high", 
        ["BTC/USD", "ETH/USD"], 
        0.85
    )
    
    await asyncio.sleep(1)  # Allow message processing
    
    # 2. Strategy Engine sends strategy signal
    print("\n2. Strategy Engine sending strategy signal...")
    await strategy_agent.send_strategy_signal(
        "trend_following",
        "BTC/USD", 
        "buy", 
        0.8
    )
    
    await asyncio.sleep(1)  # Allow message processing
    
    # 3. Check communication hub status
    print("\n3. Communication Hub Status:")
    status = comm_hub.get_communication_status()
    print(f"   Registered agents: {status['registered_agents']}")
    print(f"   Active agents: {status['active_agents']}")
    print(f"   Messages routed: {status['metrics']['messages_routed']}")
    
    # Wait for heartbeats
    await asyncio.sleep(5)
    
    # Stop agents
    strategy_agent.is_running = False
    market_agent.is_running = False
    risk_agent.is_running = False
    
    # Stop communication hub
    await comm_hub.stop()
    
    print("\nCommunication Integration Test Completed!")

if __name__ == "__main__":
    asyncio.run(test_communication_integration())
