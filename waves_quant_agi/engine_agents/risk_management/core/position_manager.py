#!/usr/bin/env python3
"""
Position Manager - CONSOLIDATED POSITION MANAGEMENT
Handles position tracking, risk assessment, and dynamic management
Integrates with Portfolio Monitor and Risk Validator
"""

import time
import asyncio
from typing import Dict, Any, List, Optional
from .portfolio_monitor import PortfolioMonitor
from .risk_validator import RiskValidator

class PositionManager:
    """
    Consolidated position management engine.
    Handles position tracking, risk assessment, and dynamic management.
    """
    
    def __init__(self, connection_manager, config: Dict[str, Any]):
        self.config = config
        self.connection_manager = connection_manager
        
        # Initialize dependencies
        self.portfolio_monitor = PortfolioMonitor(connection_manager, config)
        self.risk_validator = RiskValidator(connection_manager, config)
        
        # Position management state
        self.active_positions = {}
        self.position_history = []
        self.max_history_length = 1000
        
        # Position management thresholds
        self.position_thresholds = config.get('position_thresholds', {
            "max_position_size": 0.25,        # 25% max single position
            "max_sector_exposure": 0.40,      # 40% max sector exposure
            "min_position_size": 0.01,        # 1% min position size
            "max_correlation": 0.8,           # 80% max correlation
            "dynamic_sltp_enabled": True,     # Enable dynamic SL/TP
            "partial_profit_enabled": True,   # Enable partial profit taking
            "trailing_stop_enabled": True     # Enable trailing stops
        })
        
        # Position management statistics
        self.stats = {
            "positions_tracked": 0,
            "positions_closed": 0,
            "risk_assessments": 0,
            "sltp_adjustments": 0,
            "partial_exits": 0,
            "trailing_stops_triggered": 0,
            "start_time": time.time()
        }
        
        # Dynamic SL/TP settings
        self.dynamic_sltp_config = {
            "volatility_adjustment": True,
            "market_regime_adjustment": True,
            "profit_lock_threshold": 0.02,    # 2% profit lock
            "loss_extension_threshold": 0.01  # 1% loss extension
        }
        
        # Partial profit taking settings
        self.partial_profit_config = {
            "profit_targets": [0.05, 0.10, 0.20],  # 5%, 10%, 20%
            "exit_percentages": [0.25, 0.25, 0.25], # 25% each
            "remaining_position": 0.25              # 25% remaining
        }
        
        # Trailing stop settings
        self.trailing_stop_config = {
            "activation_threshold": 0.02,     # 2% profit to activate
            "trailing_distance": 0.01,        # 1% trailing distance
            "lock_profit_threshold": 0.05     # 5% profit to lock
        }
    
    async def add_position(self, position_data: Dict[str, Any]) -> bool:
        """Add a new position to tracking."""
        try:
            position_id = position_data.get('position_id')
            if not position_id:
                return False
            
            # Validate position data
            if not self._validate_position_data(position_data):
                return False
            
            # Initialize position tracking
            position_tracking = {
                'position_id': position_id,
                'symbol': position_data.get('symbol', ''),
                'side': position_data.get('side', ''),
                'size': position_data.get('size', 0.0),
                'entry_price': position_data.get('entry_price', 0.0),
                'current_price': position_data.get('current_price', 0.0),
                'stop_loss': position_data.get('stop_loss', 0.0),
                'take_profit': position_data.get('take_profit', 0.0),
                'entry_time': time.time(),
                'last_update': time.time(),
                'unrealized_pnl': 0.0,
                'realized_pnl': 0.0,
                'risk_score': 0.0,
                'correlation_risk': 0.0,
                'volatility': 0.0,
                'market_regime': 'normal',
                'partial_exits': [],
                'trailing_stop_active': False,
                'trailing_stop_price': 0.0,
                'status': 'active'
            }
            
            # Calculate initial risk metrics
            await self._calculate_position_risk(position_tracking)
            
            # Add to active positions
            self.active_positions[position_id] = position_tracking
            self.stats["positions_tracked"] += 1
            
            # Add to history
            self._add_to_history(position_tracking)
            
            return True
            
        except Exception as e:
            print(f"Error adding position: {e}")
            return False
    
    async def update_position(self, position_id: str, update_data: Dict[str, Any]) -> bool:
        """Update position data."""
        try:
            if position_id not in self.active_positions:
                return False
            
            position = self.active_positions[position_id]
            
            # Update position data
            for key, value in update_data.items():
                if key in position:
                    position[key] = value
            
            position['last_update'] = time.time()
            
            # Recalculate risk metrics
            await self._calculate_position_risk(position)
            
            # Check for dynamic adjustments
            await self._check_dynamic_adjustments(position)
            
            # Update history
            self._add_to_history(position)
            
            return True
            
        except Exception as e:
            print(f"Error updating position: {e}")
            return False
    
    async def close_position(self, position_id: str, close_data: Dict[str, Any]) -> bool:
        """Close a position."""
        try:
            if position_id not in self.active_positions:
                return False
            
            position = self.active_positions[position_id]
            
            # Update final data
            position.update(close_data)
            position['status'] = 'closed'
            position['close_time'] = time.time()
            position['last_update'] = time.time()
            
            # Calculate final P&L
            await self._calculate_final_pnl(position)
            
            # Add to history
            self._add_to_history(position)
            
            # Remove from active positions
            del self.active_positions[position_id]
            self.stats["positions_closed"] += 1
            
            return True
            
        except Exception as e:
            print(f"Error closing position: {e}")
            return False
    
    async def assess_portfolio_risk(self) -> Dict[str, Any]:
        """Assess overall portfolio risk."""
        try:
            risk_assessment = {
                'total_positions': len(self.active_positions),
                'total_exposure': 0.0,
                'concentration_risk': 0.0,
                'correlation_risk': 0.0,
                'volatility_risk': 0.0,
                'overall_risk_score': 0.0,
                'risk_alerts': [],
                'timestamp': time.time()
            }
            
            if not self.active_positions:
                return risk_assessment
            
            # Calculate total exposure
            total_exposure = sum(pos.get('size', 0) for pos in self.active_positions.values())
            risk_assessment['total_exposure'] = total_exposure
            
            # Assess concentration risk
            risk_assessment['concentration_risk'] = await self._assess_concentration_risk()
            
            # Assess correlation risk
            risk_assessment['correlation_risk'] = await self._assess_correlation_risk()
            
            # Assess volatility risk
            risk_assessment['volatility_risk'] = await self._assess_volatility_risk()
            
            # Calculate overall risk score
            risk_assessment['overall_risk_score'] = (
                risk_assessment['concentration_risk'] * 0.4 +
                risk_assessment['correlation_risk'] * 0.3 +
                risk_assessment['volatility_risk'] * 0.3
            )
            
            # Generate risk alerts
            risk_assessment['risk_alerts'] = await self._generate_risk_alerts(risk_assessment)
            
            self.stats["risk_assessments"] += 1
            
            return risk_assessment
            
        except Exception as e:
            print(f"Error assessing portfolio risk: {e}")
            return {}
    
    async def get_position_summary(self) -> Dict[str, Any]:
        """Get summary of all positions."""
        try:
            summary = {
                'active_positions': len(self.active_positions),
                'total_unrealized_pnl': 0.0,
                'total_realized_pnl': 0.0,
                'average_risk_score': 0.0,
                'positions_by_symbol': {},
                'positions_by_side': {'long': 0, 'short': 0},
                'timestamp': time.time()
            }
            
            if not self.active_positions:
                return summary
            
            # Calculate totals
            total_unrealized = 0.0
            total_realized = 0.0
            total_risk_score = 0.0
            
            for position in self.active_positions.values():
                total_unrealized += position.get('unrealized_pnl', 0.0)
                total_realized += position.get('realized_pnl', 0.0)
                total_risk_score += position.get('risk_score', 0.0)
                
                # Count by symbol
                symbol = position.get('symbol', 'unknown')
                if symbol not in summary['positions_by_symbol']:
                    summary['positions_by_symbol'][symbol] = 0
                summary['positions_by_symbol'][symbol] += 1
                
                # Count by side
                side = position.get('side', 'unknown')
                if side in summary['positions_by_side']:
                    summary['positions_by_side'][side] += 1
            
            summary['total_unrealized_pnl'] = total_unrealized
            summary['total_realized_pnl'] = total_realized
            summary['average_risk_score'] = total_risk_score / len(self.active_positions)
            
            return summary
            
        except Exception as e:
            print(f"Error getting position summary: {e}")
            return {}
    
    def _validate_position_data(self, position_data: Dict[str, Any]) -> bool:
        """Validate position data."""
        required_fields = ['position_id', 'symbol', 'side', 'size', 'entry_price']
        
        for field in required_fields:
            if field not in position_data:
                return False
        
        if position_data['size'] <= 0:
            return False
        
        if position_data['entry_price'] <= 0:
            return False
        
        return True
    
    async def _calculate_position_risk(self, position: Dict[str, Any]):
        """Calculate position-specific risk metrics."""
        try:
            # Mock risk calculation - replace with actual implementation
            position['risk_score'] = 0.5  # Mock value
            position['correlation_risk'] = 0.3  # Mock value
            position['volatility'] = 0.15  # Mock value
            
        except Exception as e:
            print(f"Error calculating position risk: {e}")
    
    async def _check_dynamic_adjustments(self, position: Dict[str, Any]):
        """Check for dynamic SL/TP adjustments."""
        try:
            if not self.position_thresholds['dynamic_sltp_enabled']:
                return
            
            # Mock dynamic adjustment logic
            # In a real system, this would adjust SL/TP based on:
            # - Market volatility
            # - Market regime
            # - Position performance
            # - Risk metrics
            
            self.stats["sltp_adjustments"] += 1
            
        except Exception as e:
            print(f"Error checking dynamic adjustments: {e}")
    
    async def _calculate_final_pnl(self, position: Dict[str, Any]):
        """Calculate final P&L for closed position."""
        try:
            entry_price = position.get('entry_price', 0)
            exit_price = position.get('exit_price', 0)
            size = position.get('size', 0)
            
            if position.get('side') == 'long':
                pnl = (exit_price - entry_price) * size
            else:
                pnl = (entry_price - exit_price) * size
            
            position['realized_pnl'] = pnl
            
        except Exception as e:
            print(f"Error calculating final P&L: {e}")
    
    async def _assess_concentration_risk(self) -> float:
        """Assess portfolio concentration risk."""
        try:
            if not self.active_positions:
                return 0.0
            
            # Calculate position sizes
            total_size = sum(pos.get('size', 0) for pos in self.active_positions.values())
            if total_size <= 0:
                return 0.0
            
            # Find largest position
            max_position_size = max(pos.get('size', 0) for pos in self.active_positions.values())
            concentration = max_position_size / total_size
            
            # Compare to threshold
            max_allowed = self.position_thresholds['max_position_size']
            
            if concentration <= max_allowed * 0.7:
                return 0.0  # Low risk
            elif concentration <= max_allowed:
                return 0.3  # Medium risk
            elif concentration <= max_allowed * 1.3:
                return 0.7  # High risk
            else:
                return 1.0  # Critical risk
                
        except Exception as e:
            print(f"Error assessing concentration risk: {e}")
            return 0.5
    
    async def _assess_correlation_risk(self) -> float:
        """Assess portfolio correlation risk."""
        try:
            # Mock correlation assessment
            # In a real system, this would calculate correlations between positions
            return 0.4  # Mock value
            
        except Exception as e:
            print(f"Error assessing correlation risk: {e}")
            return 0.5
    
    async def _assess_volatility_risk(self) -> float:
        """Assess portfolio volatility risk."""
        try:
            if not self.active_positions:
                return 0.0
            
            # Calculate average volatility
            total_volatility = sum(pos.get('volatility', 0) for pos in self.active_positions.values())
            avg_volatility = total_volatility / len(self.active_positions)
            
            # Normalize to 0-1 scale
            normalized_volatility = min(1.0, avg_volatility / 0.5)  # 50% volatility = max risk
            
            return normalized_volatility
            
        except Exception as e:
            print(f"Error assessing volatility risk: {e}")
            return 0.5
    
    async def _generate_risk_alerts(self, risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate risk alerts based on assessment."""
        alerts = []
        
        try:
            # Concentration risk alert
            if risk_assessment['concentration_risk'] > 0.7:
                alerts.append("High concentration risk detected")
            
            # Correlation risk alert
            if risk_assessment['correlation_risk'] > 0.7:
                alerts.append("High correlation risk detected")
            
            # Volatility risk alert
            if risk_assessment['volatility_risk'] > 0.7:
                alerts.append("High volatility risk detected")
            
            # Overall risk alert
            if risk_assessment['overall_risk_score'] > 0.8:
                alerts.append("Critical portfolio risk level")
            
        except Exception as e:
            print(f"Error generating risk alerts: {e}")
        
        return alerts
    
    def _add_to_history(self, position: Dict[str, Any]):
        """Add position to history."""
        try:
            self.position_history.append(position.copy())
            
            # Keep history within limit
            if len(self.position_history) > self.max_history_length:
                self.position_history.pop(0)
                
        except Exception as e:
            print(f"Error adding to history: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get position manager statistics."""
        return {
            **self.stats,
            'uptime': time.time() - self.stats['start_time'],
            'active_positions': len(self.active_positions),
            'history_length': len(self.position_history)
        }
