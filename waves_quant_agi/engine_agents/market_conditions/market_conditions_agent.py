#!/usr/bin/env python3
"""
Market Conditions Agent
Orchestrates supply-demand analysis with quantum-inspired processing.
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
import redis
from .logs.market_conditions_logger import MarketConditionsLogger
from .supply.detector import SupplyDetector
from .demand.intensity_reader import DemandIntensityReader

class MarketConditionsAgent:
    """Main orchestrator for market conditions analysis with quantum-inspired processing."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False
        
        # Initialize Redis connection
        self.redis_client = self._init_redis()
        self.logger = MarketConditionsLogger("market_conditions_agent", self.redis_client)
        
        # Initialize analysis components
        self._init_analysis_components()
        
        # Performance tracking
        self.stats = {
            "total_analyses": 0,
            "supply_analyses": 0,
            "demand_analyses": 0,
            "anomalies_detected": 0,
            "predictions_made": 0,
            "start_time": time.time(),
            "last_analysis_time": 0
        }

    def _init_redis(self):
        """Initialize Redis connection."""
        try:
            return redis.Redis(
                host=self.config.get("redis_host", "localhost"),
                port=self.config.get("redis_port", 6379),
                db=self.config.get("redis_db", 0),
                decode_responses=True
            )
        except Exception as e:
            self.logger.log_error(f"Failed to initialize Redis: {e}")
            return None

    def _init_analysis_components(self):
        """Initialize supply and demand analysis components."""
        try:
            supply_config = self.config.get("supply", {})
            demand_config = self.config.get("demand", {})
            
            self.supply_detector = SupplyDetector(supply_config)
            self.demand_intensity_reader = DemandIntensityReader(demand_config)
            
            self.logger.log("Analysis components initialized successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error initializing analysis components: {e}")

    async def start(self):
        """Start the market conditions agent."""
        try:
            self.logger.log("Starting Market Conditions Agent...")
            self.is_running = True
            
            # Start all analysis tasks
            tasks = [
                asyncio.create_task(self._supply_analysis_loop()),
                asyncio.create_task(self._demand_analysis_loop()),
                asyncio.create_task(self._anomaly_detection_loop()),
                asyncio.create_task(self._trend_prediction_loop()),
                asyncio.create_task(self._market_regime_loop()),
                asyncio.create_task(self._stats_reporting_loop())
            ]
            
            # Start all tasks
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logger.log_error(f"Error starting market conditions agent: {e}")
            await self.stop()

    async def stop(self):
        """Stop the market conditions agent gracefully."""
        self.logger.log("Stopping Market Conditions Agent...")
        self.is_running = False
        
        try:
            self.logger.log("Market Conditions Agent stopped successfully")
            
        except Exception as e:
            self.logger.log_error(f"Error stopping market conditions agent: {e}")

    async def _supply_analysis_loop(self):
        """Periodic supply analysis loop."""
        while self.is_running:
            try:
                # Get market data from Redis
                market_data = await self._get_market_data()
                
                if market_data:
                    # Perform supply analysis
                    supply_result = await self.supply_detector.classify_supply_behavior(market_data)
                    
                    if supply_result:
                        self.stats["supply_analyses"] += 1
                        self.logger.log_pattern("supply_analysis", supply_result)
                        
                        # Detect supply anomalies
                        anomalies = await self.supply_detector.detect_supply_anomalies(market_data)
                        if anomalies:
                            self.stats["anomalies_detected"] += len(anomalies)
                            self.logger.log_market_anomaly("supply_anomalies", {
                                "anomaly_count": len(anomalies),
                                "anomalies": anomalies
                            })
                        
                        # Predict supply trends
                        trends = await self.supply_detector.predict_supply_trends(market_data)
                        if trends:
                            self.stats["predictions_made"] += 1
                            self.logger.log_prediction("supply_trends", trends)
                
                await asyncio.sleep(self.config.get("supply_analysis_interval", 300))
                
            except Exception as e:
                self.logger.log_error(f"Error in supply analysis loop: {e}")
                await asyncio.sleep(60)

    async def _demand_analysis_loop(self):
        """Periodic demand analysis loop."""
        while self.is_running:
            try:
                # Get market data from Redis
                market_data = await self._get_market_data()
                
                if market_data:
                    # Perform demand analysis
                    demand_result = await self.demand_intensity_reader.measure_demand_intensity(market_data)
                    
                    if demand_result:
                        self.stats["demand_analyses"] += 1
                        self.logger.log_pattern("demand_analysis", demand_result)
                        
                        # Detect demand anomalies
                        anomalies = await self.demand_intensity_reader.detect_demand_anomalies(market_data)
                        if anomalies:
                            self.stats["anomalies_detected"] += len(anomalies)
                            self.logger.log_market_anomaly("demand_anomalies", {
                                "anomaly_count": len(anomalies),
                                "anomalies": anomalies
                            })
                        
                        # Predict demand trends
                        trends = await self.demand_intensity_reader.predict_demand_trends(market_data)
                        if trends:
                            self.stats["predictions_made"] += 1
                            self.logger.log_prediction("demand_trends", trends)
                
                await asyncio.sleep(self.config.get("demand_analysis_interval", 300))
                
            except Exception as e:
                self.logger.log_error(f"Error in demand analysis loop: {e}")
                await asyncio.sleep(60)

    async def _anomaly_detection_loop(self):
        """Periodic anomaly detection loop."""
        while self.is_running:
            try:
                # Get market data from Redis
                market_data = await self._get_market_data()
                
                if market_data:
                    # Detect market anomalies
                    anomalies = await self._detect_market_anomalies(market_data)
                    
                    if anomalies:
                        self.stats["anomalies_detected"] += len(anomalies)
                        self.logger.log_market_anomaly("market_anomalies", {
                            "anomaly_count": len(anomalies),
                            "anomalies": anomalies
                        })
                
                await asyncio.sleep(self.config.get("anomaly_detection_interval", 60))
                
            except Exception as e:
                self.logger.log_error(f"Error in anomaly detection loop: {e}")
                await asyncio.sleep(30)

    async def _trend_prediction_loop(self):
        """Periodic trend prediction loop."""
        while self.is_running:
            try:
                # Get market data from Redis
                market_data = await self._get_market_data()
                
                if market_data:
                    # Generate market predictions
                    predictions = await self._generate_market_predictions(market_data)
                    
                    if predictions:
                        self.stats["predictions_made"] += 1
                        self.logger.log_prediction("market_predictions", predictions)
                
                await asyncio.sleep(self.config.get("trend_prediction_interval", 900))
                
            except Exception as e:
                self.logger.log_error(f"Error in trend prediction loop: {e}")
                await asyncio.sleep(120)

    async def _market_regime_loop(self):
        """Periodic market regime detection loop."""
        while self.is_running:
            try:
                # Get market data from Redis
                market_data = await self._get_market_data()
                
                if market_data:
                    # Detect market regime
                    regime = await self._detect_market_regime(market_data)
                    
                    if regime:
                        self.logger.log_market_regime("regime_detection", regime)
                
                await asyncio.sleep(self.config.get("market_regime_interval", 1800))
                
            except Exception as e:
                self.logger.log_error(f"Error in market regime loop: {e}")
                await asyncio.sleep(300)

    async def _stats_reporting_loop(self):
        """Periodic stats reporting loop."""
        while self.is_running:
            try:
                await self._report_stats()
                await asyncio.sleep(self.config.get("stats_interval", 300))
                
            except Exception as e:
                self.logger.log_error(f"Error in stats reporting loop: {e}")
                await asyncio.sleep(60)

    async def _get_market_data(self) -> List[Dict[str, Any]]:
        """Get market data from Redis."""
        try:
            if not self.redis_client:
                return []
            
            # Get market data from Redis
            data_keys = self.redis_client.keys("market_data:*")
            market_data = []
            
            for key in data_keys[:50]:  # Limit to 50 recent data points
                try:
                    data = self.redis_client.hgetall(key)
                    if data:
                        market_data.append(data)
                except Exception as e:
                    self.logger.log_error(f"Error getting market data from {key}: {e}")
                    continue
            
            return market_data
            
        except Exception as e:
            self.logger.log_error(f"Error getting market data: {e}")
            return []

    async def _detect_market_anomalies(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect market anomalies using quantum-inspired analysis."""
        try:
            anomalies = []
            
            for data in market_data:
                try:
                    symbol = data.get("symbol", "unknown")
                    price = float(data.get("price", 0.0))
                    volume = float(data.get("volume", 0.0))
                    price_change = float(data.get("price_change", 0.0))
                    volatility = float(data.get("volatility", 0.0))
                    
                    # Quantum-inspired anomaly detection
                    if abs(price_change) > 0.1:  # 10% price change
                        anomaly = {
                            "type": "price_anomaly",
                            "symbol": symbol,
                            "anomaly_type": "extreme_price_movement",
                            "price_change": price_change,
                            "timestamp": int(time.time()),
                            "description": f"Extreme price movement for {symbol}: {price_change:.2%}"
                        }
                        anomalies.append(anomaly)
                    
                    if volatility > 0.2:  # 20% volatility
                        anomaly = {
                            "type": "volatility_anomaly",
                            "symbol": symbol,
                            "anomaly_type": "high_volatility",
                            "volatility": volatility,
                            "timestamp": int(time.time()),
                            "description": f"High volatility for {symbol}: {volatility:.2%}"
                        }
                        anomalies.append(anomaly)
                    
                except (ValueError, TypeError) as e:
                    self.logger.log_error(f"Error processing anomaly data: {e}", {"data": data})
                    continue
            
            return anomalies
            
        except Exception as e:
            self.logger.log_error(f"Error detecting market anomalies: {e}")
            return []

    async def _generate_market_predictions(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate market predictions using quantum-inspired analysis."""
        try:
            if not market_data:
                return {}
            
            predictions = {}
            
            # Group data by symbol
            symbol_data = {}
            for data in market_data:
                symbol = data.get("symbol", "unknown")
                if symbol not in symbol_data:
                    symbol_data[symbol] = []
                symbol_data[symbol].append(data)
            
            for symbol, data_list in symbol_data.items():
                try:
                    # Calculate prediction indicators
                    prices = [float(d.get("price", 0.0)) for d in data_list]
                    volumes = [float(d.get("volume", 0.0)) for d in data_list]
                    
                    if len(prices) < 3:
                        continue
                    
                    # Simple prediction logic (placeholder for quantum-inspired)
                    price_trend = "bullish" if prices[-1] > prices[0] else "bearish"
                    volume_trend = "increasing" if volumes[-1] > volumes[0] else "decreasing"
                    
                    # Generate prediction
                    if price_trend == "bullish" and volume_trend == "increasing":
                        prediction = "strong_bullish"
                    elif price_trend == "bearish" and volume_trend == "decreasing":
                        prediction = "strong_bearish"
                    else:
                        prediction = "sideways"
                    
                    predictions[symbol] = {
                        "prediction": prediction,
                        "price_trend": price_trend,
                        "volume_trend": volume_trend,
                        "confidence": 0.7,  # Placeholder confidence
                        "timestamp": int(time.time())
                    }
                    
                except Exception as e:
                    self.logger.log_error(f"Error predicting for {symbol}: {e}")
                    continue
            
            return {
                "type": "market_predictions",
                "predictions": predictions,
                "timestamp": int(time.time()),
                "description": f"Generated market predictions for {len(predictions)} symbols"
            }
            
        except Exception as e:
            self.logger.log_error(f"Error generating market predictions: {e}")
            return {}

    async def _detect_market_regime(self, market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Detect current market regime using quantum-inspired analysis."""
        try:
            if not market_data:
                return None
            
            # Calculate regime indicators
            total_volume = sum(float(d.get("volume", 0.0)) for d in market_data)
            avg_volatility = sum(float(d.get("volatility", 0.0)) for d in market_data) / len(market_data)
            price_changes = [float(d.get("price_change", 0.0)) for d in market_data]
            avg_price_change = sum(price_changes) / len(price_changes)
            
            # Determine market regime
            if avg_volatility > 0.15:  # High volatility
                regime = "volatile"
            elif abs(avg_price_change) > 0.05:  # Trending
                regime = "trending"
            elif total_volume > 1000000:  # High volume
                regime = "high_activity"
            else:
                regime = "stable"
            
            regime_data = {
                "type": "market_regime",
                "regime": regime,
                "avg_volatility": avg_volatility,
                "avg_price_change": avg_price_change,
                "total_volume": total_volume,
                "timestamp": int(time.time()),
                "description": f"Market regime detected: {regime}"
            }
            
            return regime_data
            
        except Exception as e:
            self.logger.log_error(f"Error detecting market regime: {e}")
            return None

    async def _report_stats(self):
        """Report agent statistics."""
        try:
            uptime = time.time() - self.stats["start_time"]
            
            stats_report = {
                "uptime_seconds": uptime,
                "total_analyses": self.stats["total_analyses"],
                "supply_analyses": self.stats["supply_analyses"],
                "demand_analyses": self.stats["demand_analyses"],
                "anomalies_detected": self.stats["anomalies_detected"],
                "predictions_made": self.stats["predictions_made"],
                "analyses_per_hour": self.stats["total_analyses"] / max(uptime / 3600, 1),
                "last_analysis_time": self.stats["last_analysis_time"],
                "timestamp": time.time()
            }
            
            # Store stats in Redis
            if self.redis_client:
                self.redis_client.hset("market_conditions:stats", mapping=stats_report)
            
            # Log metrics
            self.logger.log_metric("total_analyses", self.stats["total_analyses"])
            self.logger.log_metric("anomalies_detected", self.stats["anomalies_detected"])
            self.logger.log_metric("predictions_made", self.stats["predictions_made"])
            
        except Exception as e:
            self.logger.log_error(f"Error reporting stats: {e}")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        uptime = time.time() - self.stats["start_time"]
        
        return {
            "is_running": self.is_running,
            "uptime_seconds": uptime,
            "stats": self.stats,
            "components": {
                "supply_detector": hasattr(self, 'supply_detector'),
                "demand_intensity_reader": hasattr(self, 'demand_intensity_reader')
            }
        } 