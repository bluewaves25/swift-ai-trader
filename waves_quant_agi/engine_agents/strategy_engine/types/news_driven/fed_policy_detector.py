#!/usr/bin/env python3
"""
Fed Policy Detector Strategy - Fixed and Enhanced
News-driven trading using Federal Reserve policy announcements.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
from engine_agents.shared_utils import get_shared_redis

class FedPolicyDetectorStrategy:
    """Fed policy detector strategy for news-driven trading."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        
        # Strategy parameters
        self.policy_impact_threshold = config.get("policy_impact_threshold", 0.7)  # 70% impact confidence
        self.reaction_window = config.get("reaction_window", 7200)  # 2 hour reaction window
        self.volatility_threshold = config.get("volatility_threshold", 2.0)  # 2x volatility increase
        self.correlation_threshold = config.get("correlation_threshold", 0.8)  # 80% correlation threshold
        self.hold_duration = config.get("hold_duration", 14400)  # 4 hour hold duration
        
        # Fed policy types
        self.policy_types = ["rate_decision", "fomc_minutes", "speech", "economic_data"]

    async def detect_opportunity(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect Fed policy reaction opportunities."""
        try:
            opportunities = []
            
            if not market_data:
                return opportunities
            
            # Get Fed policy announcements from news feeds
            policy_announcements = await self._get_policy_announcements()
            
            for announcement in policy_announcements:
                opportunity = await self._check_policy_reaction(announcement, market_data)
                if opportunity:
                    opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting Fed policy opportunities: {e}")
            return []

    async def _get_policy_announcements(self) -> List[Dict[str, Any]]:
        """Get Fed policy announcements from news feeds."""
        try:
            if not self.redis_conn:
                return []
            
            # Get policy announcements from news feeds
            policy_key = "news_feeds:fed_policy_announcements"
            policy_data = self.redis_conn.get(policy_key)
            
            if policy_data:
                import json
                return json.loads(policy_data)
            
            return []
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting policy announcements: {e}")
            return []

    async def _check_policy_reaction(self, announcement: Dict[str, Any], 
                                   market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Check for Fed policy reaction opportunity."""
        try:
            policy_type = announcement.get("policy_type", "")
            impact_score = float(announcement.get("impact_score", 0.0))
            announcement_time = announcement.get("announcement_time", 0)
            
            if not policy_type or impact_score < self.policy_impact_threshold:
                return None
            
            # Check if announcement is recent
            current_time = time.time()
            if current_time - announcement_time > self.reaction_window:
                return None
            
            # Get affected assets
            affected_assets = await self._get_affected_assets(announcement)
            
            opportunities = []
            for asset in affected_assets:
                opportunity = await self._create_policy_opportunity(asset, announcement, market_data)
                if opportunity:
                    opportunities.append(opportunity)
            
            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error checking policy reaction: {e}")
            return None

    async def _get_affected_assets(self, announcement: Dict[str, Any]) -> List[str]:
        """Get assets affected by the policy announcement."""
        try:
            policy_type = announcement.get("policy_type", "")
            
            # Get available assets from data feeds
            available_assets = await self._get_available_assets()
            
            # Filter assets based on policy type
            if policy_type == "rate_decision":
                # Interest rate decisions affect forex and bonds
                return [asset for asset in available_assets if any(currency in asset for currency in ["USD", "EUR", "GBP", "JPY"])]
            elif policy_type == "fomc_minutes":
                # FOMC minutes affect broader markets
                return available_assets[:10]  # Top 10 assets
            elif policy_type == "speech":
                # Speeches can affect any asset
                return available_assets[:5]  # Top 5 assets
            else:
                # Economic data affects specific sectors
                return available_assets[:3]  # Top 3 assets
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting affected assets: {e}")
            return []

    async def _get_available_assets(self) -> List[str]:
        """Get available assets from data feeds."""
        try:
            if not self.redis_conn:
                return []
            
            # Get available symbols from data feeds
            symbols_key = "data_feeds:available_symbols"
            symbols_data = self.redis_conn.get(symbols_key)
            
            if symbols_data:
                import json
                return json.loads(symbols_data)
            
            return []
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting available assets: {e}")
            return []

    async def _create_policy_opportunity(self, asset: str, announcement: Dict[str, Any], 
                                       market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Create policy reaction opportunity for an asset."""
        try:
            # Get current market data for asset
            asset_data = await self._get_symbol_market_data(asset, market_data)
            if not asset_data:
                return None
            
            # Calculate policy impact metrics
            impact_metrics = await self._calculate_policy_impact(asset, announcement, asset_data)
            
            if not impact_metrics['opportunity_detected']:
                return None
            
            # Determine trade direction based on policy type and impact
            action = await self._determine_policy_action(announcement, impact_metrics)
            
            current_price = float(asset_data.get("close", 0.0))
            if current_price <= 0:
                return None
            
            opportunity = {
                "type": "fed_policy_detector",
                "strategy": "news_driven",
                "symbol": asset,
                "action": action,
                "entry_price": current_price,
                "stop_loss": current_price * (1 - 0.02 if action == "buy" else 1 + 0.02),
                "take_profit": current_price * (1 + 0.03 if action == "buy" else 1 - 0.03),
                "confidence": impact_metrics['impact_confidence'],
                "policy_type": announcement.get("policy_type", ""),
                "impact_score": announcement.get("impact_score", 0.0),
                "volatility_change": impact_metrics['volatility_change'],
                "correlation_change": impact_metrics['correlation_change'],
                "announcement_time": announcement.get("announcement_time", 0),
                "hold_duration": self.hold_duration,
                "timestamp": int(time.time()),
                "description": f"Fed policy reaction for {asset}: {announcement.get('policy_type', '')}, Action {action}"
            }
            
            # Store in Redis
            if self.redis_conn:
                try:
                    import json
                    self.redis_conn.set(
                        f"strategy_engine:fed_policy:{asset}:{int(time.time())}", 
                        json.dumps(opportunity), 
                        ex=3600
                    )
                except json.JSONEncodeError as e:
                    if self.logger:
                        self.logger.error(f"JSON encoding error storing fed policy impact: {e}")
                except ConnectionError as e:
                    if self.logger:
                        self.logger.error(f"Redis connection error storing fed policy impact: {e}")
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Unexpected error storing fed policy impact: {e}")
            
            if self.logger:
                self.logger.info(f"Fed policy opportunity: {opportunity['description']}")
            
            return opportunity
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error creating policy opportunity: {e}")
            return None

    async def _get_symbol_market_data(self, symbol: str, market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Get market data for a specific symbol."""
        try:
            for data in market_data:
                if data.get("symbol") == symbol:
                    return data
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting symbol market data: {e}")
            return None

    async def _calculate_policy_impact(self, asset: str, announcement: Dict[str, Any], 
                                     asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Fed policy impact metrics."""
        try:
            # Get historical data for comparison
            historical_data = await self._get_historical_data(asset)
            
            if historical_data is None:
                return {
                    "opportunity_detected": False,
                    "impact_confidence": 0.0,
                    "volatility_change": 1.0,
                    "correlation_change": 0.0
                }
            
            # Calculate volatility change
            current_volatility = asset_data.get("volatility", 0.0)
            historical_volatility = historical_data['close'].pct_change().std() if len(historical_data) > 1 else 0.0
            
            volatility_change = current_volatility / historical_volatility if historical_volatility > 0 else 1.0
            
            # Calculate correlation change (simplified)
            correlation_change = 0.5  # Placeholder for correlation calculation
            
            # Determine if opportunity exists
            volatility_threshold_met = volatility_change > self.volatility_threshold
            impact_threshold_met = announcement.get("impact_score", 0.0) > self.policy_impact_threshold
            
            opportunity_detected = volatility_threshold_met and impact_threshold_met
            
            # Calculate impact confidence
            impact_confidence = min(
                (announcement.get("impact_score", 0.0) / self.policy_impact_threshold) * 
                (volatility_change / self.volatility_threshold), 
                0.9
            )
            
            return {
                "opportunity_detected": opportunity_detected,
                "impact_confidence": impact_confidence,
                "volatility_change": volatility_change,
                "correlation_change": correlation_change
            }
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error calculating policy impact: {e}")
            return {
                "opportunity_detected": False,
                "impact_confidence": 0.0,
                "volatility_change": 1.0,
                "correlation_change": 0.0
            }

    async def _determine_policy_action(self, announcement: Dict[str, Any], 
                                     impact_metrics: Dict[str, Any]) -> str:
        """Determine trade action based on policy announcement."""
        try:
            policy_type = announcement.get("policy_type", "")
            impact_score = announcement.get("impact_score", 0.0)
            
            # Simple rule-based action determination
            if policy_type == "rate_decision":
                if impact_score > 0.8:  # High impact
                    return "buy" if impact_score > 0.9 else "sell"
                else:
                    return "hold"
            elif policy_type == "fomc_minutes":
                return "buy" if impact_score > 0.7 else "hold"
            elif policy_type == "speech":
                return "buy" if impact_score > 0.6 else "hold"
            else:
                return "hold"
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error determining policy action: {e}")
            return "hold"

    async def _get_historical_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Get historical data for a symbol."""
        try:
            if not self.redis_conn:
                return None
            
            historical_key = f"market_data:{symbol}:history"
            historical_data = self.redis_conn.get(historical_key)
            
            if historical_data:
                import json
                return pd.DataFrame(json.loads(historical_data))
            
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting historical data for {symbol}: {e}")
            return None

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Fed Policy Detector Strategy",
            "type": "news_driven",
            "description": "News-driven trading using Federal Reserve policy announcements",
            "parameters": {
                "policy_impact_threshold": self.policy_impact_threshold,
                "reaction_window": self.reaction_window,
                "volatility_threshold": self.volatility_threshold,
                "correlation_threshold": self.correlation_threshold,
                "hold_duration": self.hold_duration
            },
            "timeframe": "tactical",  # 30s tier
            "asset_types": ["forex", "indices", "bonds"],
            "execution_speed": "medium"
        }