import time
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import redis
from ..logs.intelligence_logger import IntelligenceLogger

class CorrelationMatrix:
    """Advanced correlation analysis for agent performance metrics and market patterns."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = self._init_redis()
        self.logger = IntelligenceLogger("correlation_matrix", self.redis_client)
        
        # Configuration parameters
        self.correlation_threshold = config.get("correlation_threshold", 0.7)
        self.min_data_points = config.get("min_data_points", 10)
        self.correlation_window = config.get("correlation_window", 3600)  # 1 hour
        self.update_interval = config.get("update_interval", 300)  # 5 minutes
        
        # Performance tracking
        self.stats = {
            "total_analyses": 0,
            "significant_correlations": 0,
            "last_analysis_time": 0,
            "start_time": time.time()
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

    async def build_correlation_matrix(self, agent_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build correlation matrix for agent performance metrics."""
        try:
            if not agent_metrics or len(agent_metrics) < self.min_data_points:
                self.logger.log_info(f"Insufficient data points for correlation analysis: {len(agent_metrics)}")
                return {}

            # Prepare DataFrame from agent metrics
            metrics_data = []
            for metric in agent_metrics:
                try:
                    metrics_data.append({
                        "agent": metric.get("agent", "unknown"),
                        "speed": float(metric.get("speed", 0.0)),
                        "accuracy": float(metric.get("accuracy", 0.0)),
                        "cost": float(metric.get("cost", 0.0)),
                        "error_rate": float(metric.get("error_rate", 0.0)),
                        "volume": float(metric.get("volume", 0.0)),
                        "latency": float(metric.get("latency", 0.0)),
                        "success_rate": float(metric.get("success_rate", 0.0))
                    })
                except (ValueError, TypeError) as e:
                    self.logger.log_error(f"Error processing metric: {e}", {"metric": metric})
                    continue

            if len(metrics_data) < self.min_data_points:
                self.logger.log_info(f"Not enough valid data points: {len(metrics_data)}")
                return {}

            metrics_df = pd.DataFrame(metrics_data)
            
            # Compute correlation matrix
            numeric_columns = metrics_df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) < 2:
                self.logger.log_error("Not enough numeric columns for correlation analysis")
                return {}

            corr_matrix = metrics_df[numeric_columns].corr()
            
            # Find significant correlations
            high_correlations = {}
            for col1 in corr_matrix.columns:
                for col2 in corr_matrix.columns:
                    if col1 != col2:
                        correlation = corr_matrix.loc[col1, col2]
                        if abs(correlation) > self.correlation_threshold:
                            high_correlations[f"{col1}_vs_{col2}"] = {
                                "correlation": float(correlation),
                                "strength": "strong" if abs(correlation) > 0.8 else "moderate",
                                "direction": "positive" if correlation > 0 else "negative"
                            }

            # Calculate additional statistics
            stats = {
                "total_metrics": len(metrics_data),
                "total_correlations": len(high_correlations),
                "mean_correlation": float(corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()),
                "std_correlation": float(corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].std())
            }

            result = {
                "type": "correlation_matrix",
                "correlations": high_correlations,
                "statistics": stats,
                "timestamp": int(time.time()),
                "description": f"Found {len(high_correlations)} significant correlations from {len(metrics_data)} data points"
            }

            # Update stats
            self.stats["total_analyses"] += 1
            self.stats["significant_correlations"] += len(high_correlations)
            self.stats["last_analysis_time"] = time.time()

            # Log and store results
            self.logger.log_pattern("correlation_matrix", result)
            
            # Store in Redis
            if self.redis_client:
                try:
                    self.redis_client.hset("intelligence:correlation_matrix", mapping=result)
                    self.redis_client.expire("intelligence:correlation_matrix", 604800)  # 7 days
                except Exception as e:
                    self.logger.log_error(f"Failed to store correlation matrix in Redis: {e}")

            # Log metrics
            self.logger.log_metric("correlation_analyses", self.stats["total_analyses"])
            self.logger.log_metric("significant_correlations", len(high_correlations))
            self.logger.log_metric("mean_correlation", stats["mean_correlation"])

            await self.notify_core(result)
            return result

        except Exception as e:
            self.logger.log_error(f"Error building correlation matrix: {e}")
            return {}

    async def analyze_market_correlations(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze correlations in market data."""
        try:
            if not market_data or len(market_data) < self.min_data_points:
                self.logger.log_info(f"Insufficient market data for correlation analysis: {len(market_data)}")
                return {}

            # Prepare market data
            market_metrics = []
            for data_point in market_data:
                try:
                    market_metrics.append({
                        "price": float(data_point.get("price", 0.0)),
                        "volume": float(data_point.get("volume", 0.0)),
                        "volatility": float(data_point.get("volatility", 0.0)),
                        "spread": float(data_point.get("spread", 0.0)),
                        "sentiment": float(data_point.get("sentiment", 0.0)),
                        "momentum": float(data_point.get("momentum", 0.0))
                    })
                except (ValueError, TypeError) as e:
                    self.logger.log_error(f"Error processing market data: {e}", {"data_point": data_point})
                    continue

            if len(market_metrics) < self.min_data_points:
                return {}

            market_df = pd.DataFrame(market_metrics)
            
            # Compute market correlations
            corr_matrix = market_df.corr()
            
            # Find significant market correlations
            market_correlations = {}
            for col1 in corr_matrix.columns:
                for col2 in corr_matrix.columns:
                    if col1 != col2:
                        correlation = corr_matrix.loc[col1, col2]
                        if abs(correlation) > self.correlation_threshold:
                            market_correlations[f"{col1}_vs_{col2}"] = {
                                "correlation": float(correlation),
                                "strength": "strong" if abs(correlation) > 0.8 else "moderate",
                                "direction": "positive" if correlation > 0 else "negative"
                            }

            result = {
                "type": "market_correlation_matrix",
                "correlations": market_correlations,
                "timestamp": int(time.time()),
                "description": f"Found {len(market_correlations)} significant market correlations"
            }

            self.logger.log_pattern("market_correlation", result)
            await self.notify_core(result)
            return result

        except Exception as e:
            self.logger.log_error(f"Error analyzing market correlations: {e}")
            return {}

    async def detect_correlation_changes(self, current_correlations: Dict[str, Any], 
                                       previous_correlations: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect significant changes in correlation patterns."""
        try:
            changes = []
            
            if not previous_correlations or "correlations" not in previous_correlations:
                return changes

            current = current_correlations.get("correlations", {})
            previous = previous_correlations.get("correlations", {})
            
            # Compare correlations
            all_keys = set(current.keys()) | set(previous.keys())
            
            for key in all_keys:
                current_corr = current.get(key, {}).get("correlation", 0)
                previous_corr = previous.get(key, {}).get("correlation", 0)
                
                change = abs(current_corr - previous_corr)
                if change > self.config.get("correlation_change_threshold", 0.2):
                    changes.append({
                        "type": "correlation_change",
                        "correlation_key": key,
                        "previous_correlation": previous_corr,
                        "current_correlation": current_corr,
                        "change": change,
                        "timestamp": int(time.time()),
                        "description": f"Significant change in {key}: {previous_corr:.3f} -> {current_corr:.3f}"
                    })

            if changes:
                self.logger.log_anomaly("correlation_changes", {
                    "change_count": len(changes),
                    "changes": changes
                })

            return changes

        except Exception as e:
            self.logger.log_error(f"Error detecting correlation changes: {e}")
            return []

    async def get_correlation_insights(self, correlations: Dict[str, Any]) -> List[str]:
        """Generate insights from correlation analysis."""
        try:
            insights = []
            
            if not correlations or "correlations" not in correlations:
                return insights

            corr_data = correlations["correlations"]
            
            # Analyze correlation patterns
            positive_correlations = [k for k, v in corr_data.items() if v.get("direction") == "positive"]
            negative_correlations = [k for k, v in corr_data.items() if v.get("direction") == "negative"]
            strong_correlations = [k for k, v in corr_data.items() if v.get("strength") == "strong"]
            
            if positive_correlations:
                insights.append(f"Found {len(positive_correlations)} positive correlations indicating synergistic relationships")
            
            if negative_correlations:
                insights.append(f"Found {len(negative_correlations)} negative correlations indicating trade-off relationships")
            
            if strong_correlations:
                insights.append(f"Found {len(strong_correlations)} strong correlations that may require attention")
            
            # Look for specific patterns
            if "speed_vs_accuracy" in corr_data:
                insight = "Speed-accuracy trade-off detected"
                if corr_data["speed_vs_accuracy"]["direction"] == "negative":
                    insight += " (faster execution may reduce accuracy)"
                insights.append(insight)
            
            if "cost_vs_error_rate" in corr_data:
                insight = "Cost-error relationship detected"
                if corr_data["cost_vs_error_rate"]["direction"] == "negative":
                    insight += " (higher costs may reduce errors)"
                insights.append(insight)

            return insights

        except Exception as e:
            self.logger.log_error(f"Error generating correlation insights: {e}")
            return []

    async def notify_core(self, result: Dict[str, Any]):
        """Notify Core Agent of correlation results."""
        try:
            self.logger.log_info(f"Notifying Core Agent: {result.get('description', 'unknown')}")
            
            # Publish to Redis for Core Agent
            if self.redis_client:
                try:
                    notification = {
                        "type": "correlation_analysis",
                        "data": result,
                        "timestamp": time.time(),
                        "source": "intelligence_correlation_matrix"
                    }
                    
                    self.redis_client.publish("core:notifications", str(notification))
                except Exception as e:
                    self.logger.log_error(f"Failed to notify Core Agent: {e}")
                    
        except Exception as e:
            self.logger.log_error(f"Error in notify_core: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get correlation matrix statistics."""
        uptime = time.time() - self.stats["start_time"]
        
        return {
            "uptime_seconds": uptime,
            "total_analyses": self.stats["total_analyses"],
            "significant_correlations": self.stats["significant_correlations"],
            "analyses_per_hour": self.stats["total_analyses"] / max(uptime / 3600, 1),
            "last_analysis_time": self.stats["last_analysis_time"],
            "correlation_threshold": self.correlation_threshold,
            "min_data_points": self.min_data_points
        }