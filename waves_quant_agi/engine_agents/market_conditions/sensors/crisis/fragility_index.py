import time
from typing import Dict, Any, List
import redis
from ...logs.failure_agent_logger import FailureAgentLogger
from ...logs.incident_cache import IncidentCache

class FragilityIndex:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.redis_client = redis.Redis(
            host=config.get("redis_host", "localhost"),
            port=config.get("redis_port", 6379),
            db=config.get("redis_db", 0),
            decode_responses=True
        )
        self.fragility_threshold = config.get("fragility_threshold", 0.7)  # Fragility score threshold

    async def calculate_fragility_index(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate real-time crisis fragility index using market stress indicators and systemic risk factors."""
        try:
            fragility_scores = []
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                volatility = float(data.get("volatility", 0.0))
                liquidity_ratio = float(data.get("liquidity_ratio", 1.0))
                volume_ratio = float(data.get("volume_ratio", 1.0))
                spread = float(data.get("spread", 0.001))
                order_imbalance = float(data.get("order_imbalance", 0.0))
                correlation_breakdown = float(data.get("correlation_breakdown", 0.0))
                market_depth = int(data.get("market_depth", 1000))
                
                # Real-time fragility analysis based on multiple stress factors
                fragility_score = self._calculate_fragility_score(
                    volatility, liquidity_ratio, volume_ratio, spread, 
                    order_imbalance, correlation_breakdown, market_depth
                )
                
                fragility_level = self._classify_fragility_level(fragility_score)
                stress_indicators = self._identify_stress_indicators(
                    volatility, liquidity_ratio, volume_ratio, spread, 
                    order_imbalance, correlation_breakdown, market_depth
                )
                
                crisis_probability = self._estimate_crisis_probability(fragility_score, stress_indicators)
                
                fragility = {
                    "type": "crisis_fragility_analysis",
                    "symbol": symbol,
                    "fragility_score": fragility_score,
                    "fragility_level": fragility_level,
                    "stress_indicators": stress_indicators,
                    "crisis_probability": crisis_probability,
                    "volatility": volatility,
                    "liquidity_ratio": liquidity_ratio,
                    "volume_ratio": volume_ratio,
                    "spread": spread,
                    "order_imbalance": order_imbalance,
                    "correlation_breakdown": correlation_breakdown,
                    "market_depth": market_depth,
                    "timestamp": int(time.time()),
                    "description": f"Crisis fragility for {symbol}: {fragility_level} (score: {fragility_score:.2f}, crisis probability: {crisis_probability:.2f})"
                }
                
                fragility_scores.append(fragility)
                self.logger.log_issue(fragility)
                self.cache.store_incident(fragility)
                self.redis_client.set(f"market_conditions:fragility:{symbol}", str(fragility), ex=604800)
            
            summary = {
                "type": "fragility_analysis_summary",
                "fragility_count": len(fragility_scores),
                "timestamp": int(time.time()),
                "description": f"Analyzed crisis fragility for {len(fragility_scores)} symbols"
            }
            self.logger.log_issue(summary)
            self.cache.store_incident(summary)
            await self.notify_core(summary)
            return fragility_scores
            
        except Exception as e:
            self.logger.log(f"Error calculating fragility index: {e}")
            self.cache.store_incident({
                "type": "fragility_analysis_error",
                "timestamp": int(time.time()),
                "description": f"Error calculating fragility index: {str(e)}"
            })
            return []
    
    def _calculate_fragility_score(self, volatility: float, liquidity_ratio: float, volume_ratio: float,
                                 spread: float, order_imbalance: float, correlation_breakdown: float, 
                                 market_depth: int) -> float:
        """Calculate real-time fragility score based on market stress indicators."""
        try:
            # Volatility stress factor (0-1)
            volatility_stress = min(1.0, volatility / 0.1)  # Normalize to 10% volatility
            
            # Liquidity stress factor (0-1)
            liquidity_stress = max(0.0, 1.0 - liquidity_ratio)
            
            # Volume stress factor (0-1)
            volume_stress = max(0.0, (volume_ratio - 1.0) / 4.0)  # Normalize to 5x volume
            
            # Spread stress factor (0-1)
            spread_stress = min(1.0, spread / 0.02)  # Normalize to 2% spread
            
            # Order imbalance stress factor (0-1)
            imbalance_stress = abs(order_imbalance)
            
            # Correlation breakdown stress factor (0-1)
            correlation_stress = min(1.0, correlation_breakdown / 0.5)  # Normalize to 50% breakdown
            
            # Market depth stress factor (0-1)
            depth_stress = max(0.0, 1.0 - (market_depth / 10000.0))  # Normalize to 10k depth
            
            # Weighted fragility score
            fragility_score = (
                volatility_stress * 0.25 +
                liquidity_stress * 0.25 +
                volume_stress * 0.15 +
                spread_stress * 0.15 +
                imbalance_stress * 0.1 +
                correlation_stress * 0.05 +
                depth_stress * 0.05
            )
            
            return max(0.0, min(1.0, fragility_score))
            
        except Exception as e:
            self.logger.log_error(f"Error calculating fragility score: {e}")
            return 0.5
    
    def _classify_fragility_level(self, fragility_score: float) -> str:
        """Classify fragility level based on calculated score."""
        try:
            if fragility_score > 0.8:
                return "critical_fragility"
            elif fragility_score > 0.6:
                return "high_fragility"
            elif fragility_score > 0.4:
                return "moderate_fragility"
            elif fragility_score > 0.2:
                return "low_fragility"
            else:
                return "stable"
                
        except Exception as e:
            self.logger.log_error(f"Error classifying fragility level: {e}")
            return "unknown"
    
    def _identify_stress_indicators(self, volatility: float, liquidity_ratio: float, volume_ratio: float,
                                  spread: float, order_imbalance: float, correlation_breakdown: float, 
                                  market_depth: int) -> List[str]:
        """Identify specific stress indicators contributing to fragility."""
        try:
            stress_indicators = []
            
            # Volatility stress
            if volatility > 0.08:
                stress_indicators.append("extreme_volatility")
            elif volatility > 0.05:
                stress_indicators.append("high_volatility")
            
            # Liquidity stress
            if liquidity_ratio < 0.3:
                stress_indicators.append("critical_liquidity_shortage")
            elif liquidity_ratio < 0.6:
                stress_indicators.append("liquidity_shortage")
            
            # Volume stress
            if volume_ratio > 5.0:
                stress_indicators.append("extreme_volume_surge")
            elif volume_ratio > 3.0:
                stress_indicators.append("volume_surge")
            
            # Spread stress
            if spread > 0.015:
                stress_indicators.append("critical_spread_widening")
            elif spread > 0.008:
                stress_indicators.append("spread_widening")
            
            # Order imbalance stress
            if abs(order_imbalance) > 0.7:
                stress_indicators.append("extreme_order_imbalance")
            elif abs(order_imbalance) > 0.5:
                stress_indicators.append("order_imbalance")
            
            # Correlation stress
            if correlation_breakdown > 0.4:
                stress_indicators.append("correlation_breakdown")
            
            # Market depth stress
            if market_depth < 2000:
                stress_indicators.append("critical_market_depth_loss")
            elif market_depth < 5000:
                stress_indicators.append("market_depth_loss")
            
            return stress_indicators if stress_indicators else ["no_significant_stress"]
            
        except Exception as e:
            self.logger.log_error(f"Error identifying stress indicators: {e}")
            return ["error_identifying_stress"]
    
    def _estimate_crisis_probability(self, fragility_score: float, stress_indicators: List[str]) -> float:
        """Estimate probability of crisis based on fragility score and stress indicators."""
        try:
            # Base probability from fragility score
            base_probability = fragility_score
            
            # Stress indicator multiplier
            critical_stress_count = sum(1 for indicator in stress_indicators if "critical" in indicator)
            high_stress_count = sum(1 for indicator in stress_indicators if "high" in indicator or "extreme" in indicator)
            
            stress_multiplier = 1.0 + (critical_stress_count * 0.3) + (high_stress_count * 0.15)
            
            # Calculate crisis probability
            crisis_probability = min(1.0, base_probability * stress_multiplier)
            
            return crisis_probability
            
        except Exception as e:
            self.logger.log_error(f"Error estimating crisis probability: {e}")
            return 0.5

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of fragility results."""
        self.logger.log(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
        self.redis_client.publish("market_conditions_output", str(issue))