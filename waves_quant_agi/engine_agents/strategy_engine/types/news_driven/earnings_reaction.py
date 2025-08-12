#!/usr/bin/env python3
"""
Earnings Reaction Strategy - Fixed and Enhanced
News-driven trading based on earnings announcements and reactions.
"""

from typing import Dict, Any, List, Optional
import time
import pandas as pd
from engine_agents.shared_utils import get_shared_redis

class EarningsReactionStrategy:
    """Earnings reaction strategy for news-driven trading."""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        self.config = config
        self.logger = logger
        # Use shared Redis connection
        self.redis_conn = get_shared_redis()
        self.earnings_surprise_threshold = config.get("earnings_surprise_threshold", 0.05)  # 5% surprise

    async def detect_earnings_signal(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect trading signals based on earnings surprises."""
        try:
            opportunities = []
            
            if not market_data:
                return opportunities
            
            # Get earnings announcements from news feeds
            earnings_announcements = await self._get_earnings_announcements()
            
            for data in market_data:
                symbol = data.get("symbol", "")
                if not symbol:
                    continue
                
                # Check if symbol has earnings announcement
                if symbol not in earnings_announcements:
                    continue
                
                earnings_surprise = float(data.get("earnings_surprise", 0.0))
                price_change = float(data.get("price_change", 0.0))

                if earnings_surprise > self.earnings_surprise_threshold and price_change > 0:
                    signal = "buy"
                    description = f"Bullish earnings reaction for {symbol}: Surprise {earnings_surprise:.2f}"
                elif earnings_surprise < -self.earnings_surprise_threshold and price_change < 0:
                    signal = "sell"
                    description = f"Bearish earnings reaction for {symbol}: Surprise {earnings_surprise:.2f}"
                else:
                    continue

                opportunity = {
                    "type": "earnings_reaction",
                    "strategy": "news_driven",
                    "symbol": symbol,
                    "signal": signal,
                    "earnings_surprise": earnings_surprise,
                    "price_change": price_change,
                    "timestamp": int(time.time()),
                    "description": description
                }
                opportunities.append(opportunity)
                
                # Store earnings reaction in Redis with proper JSON serialization
                if self.redis_conn:
                    try:
                        import json
                        self.redis_conn.set(
                            f"strategy_engine:earnings_reaction:{symbol}:{int(time.time())}", 
                            json.dumps(opportunity), 
                            ex=3600
                        )
                    except json.JSONEncodeError as e:
                        if self.logger:
                            self.logger.error(f"JSON encoding error storing earnings reaction: {e}")
                    except ConnectionError as e:
                        if self.logger:
                            self.logger.error(f"Redis connection error storing earnings reaction: {e}")
                    except Exception as e:
                        if self.logger:
                            self.logger.error(f"Unexpected error storing earnings reaction: {e}")
                
                if self.logger:
                    self.logger.info(f"Earnings reaction opportunity: {opportunity['description']}")

            return opportunities
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error detecting earnings reaction: {e}")
            return []

    async def _get_earnings_announcements(self) -> Dict[str, Dict[str, Any]]:
        """Get earnings announcements from news feeds."""
        try:
            if not self.redis_conn:
                return {}
            
            # Get earnings announcements from news feeds
            earnings_key = "news_feeds:earnings_announcements"
            earnings_data = self.redis_conn.get(earnings_key)
            
            if earnings_data:
                import json
                return json.loads(earnings_data)
            
            return {}
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error getting earnings announcements: {e}")
            return {}

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": "Earnings Reaction Strategy",
            "type": "news_driven",
            "description": "News-driven trading based on earnings announcements and reactions",
            "parameters": {
                "earnings_surprise_threshold": self.earnings_surprise_threshold
            },
            "timeframe": "tactical",  # 30s tier
            "asset_types": ["stocks"],
            "execution_speed": "fast"
        }