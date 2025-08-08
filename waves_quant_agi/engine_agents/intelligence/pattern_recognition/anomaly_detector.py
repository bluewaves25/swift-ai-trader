import time
from typing import Dict, Any, List, Optional
import statistics
import numpy as np
import pandas as pd
from ..logs.intelligence_logger import IntelligenceLogger

class AnomalyDetector:
    """Advanced anomaly detection for agent performance and market patterns."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = IntelligenceLogger("anomaly_detector")
        
        # Configuration parameters
        self.anomaly_threshold = config.get("anomaly_threshold", 2.0)  # 2 standard deviations
        self.min_data_points = config.get("min_data_points", 10)
        self.detection_window = config.get("detection_window", 3600)  # 1 hour
        self.update_interval = config.get("update_interval", 60)  # 1 minute
        
        # Performance tracking
        self.stats = {
            "total_detections": 0,
            "anomalies_found": 0,
            "last_detection_time": 0,
            "start_time": time.time()
        }

    async def detect_anomalies(self, agent_metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in agent performance metrics."""
        try:
            if not agent_metrics or len(agent_metrics) < self.min_data_points:
                self.logger.log_info(f"Insufficient data points for anomaly detection: {len(agent_metrics)}")
                return []

            anomalies = []
            metric_types = ["speed", "accuracy", "cost", "error_rate", "volume", "latency", "success_rate"]
            
            for metric_type in metric_types:
                try:
                    # Extract valid values for the metric type
                    values = []
                    for metric in agent_metrics:
                        value = metric.get(metric_type, 0.0)
                        if value is not None and value > 0:
                            try:
                                values.append(float(value))
                            except (ValueError, TypeError):
                                continue
                    
                    if len(values) < self.min_data_points:
                        continue

                    # Calculate statistics
                    mean = statistics.mean(values)
                    stdev = statistics.stdev(values) if len(values) > 1 else 0
                    
                    if stdev == 0:
                        continue
                    
                    # Define thresholds
                    upper_threshold = mean + self.anomaly_threshold * stdev
                    lower_threshold = mean - self.anomaly_threshold * stdev

                    # Detect anomalies
                    for metric in agent_metrics:
                        try:
                            value = float(metric.get(metric_type, 0.0))
                            if value > 0:  # Only check non-zero values
                                if value > upper_threshold or value < lower_threshold:
                                    anomaly = {
                                        "type": "agent_anomaly",
                                        "agent": metric.get("agent", "unknown"),
                                        "metric_type": metric_type,
                                        "value": value,
                                        "mean": mean,
                                        "stdev": stdev,
                                        "upper_threshold": upper_threshold,
                                        "lower_threshold": lower_threshold,
                                        "severity": "high" if abs(value - mean) > 3 * stdev else "medium",
                                        "timestamp": int(time.time()),
                                        "description": f"Anomaly in {metric_type} for {metric.get('agent')}: {value:.4f} (mean: {mean:.4f}, std: {stdev:.4f})"
                                    }
                                    anomalies.append(anomaly)
                                    self.logger.log_anomaly("agent_anomaly", anomaly)
                        except (ValueError, TypeError) as e:
                            self.logger.log_error(f"Error processing metric value: {e}", {"metric": metric})
                            continue

                except Exception as e:
                    self.logger.log_error(f"Error processing metric type {metric_type}: {e}")
                    continue

            # Update stats
            self.stats["total_detections"] += 1
            self.stats["anomalies_found"] += len(anomalies)
            self.stats["last_detection_time"] = time.time()

            # Log results
            if anomalies:
                result = {
                    "type": "anomaly_detection",
                    "anomaly_count": len(anomalies),
                    "anomalies": anomalies,
                    "timestamp": int(time.time()),
                    "description": f"Detected {len(anomalies)} agent performance anomalies"
                }
                self.logger.log_anomaly("anomaly_detection_summary", result)
                await self.notify_core(result)

            # Log metrics
            self.logger.log_metric("anomaly_detections", self.stats["total_detections"])
            self.logger.log_metric("anomalies_found", len(anomalies))

            return anomalies

        except Exception as e:
            self.logger.log_error(f"Error detecting anomalies: {e}")
            return []

    async def detect_market_anomalies(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in market data."""
        try:
            if not market_data or len(market_data) < self.min_data_points:
                self.logger.log_info(f"Insufficient market data for anomaly detection: {len(market_data)}")
                return []

            anomalies = []
            market_metrics = ["price", "volume", "volatility", "spread", "sentiment", "momentum"]
            
            for metric_type in market_metrics:
                try:
                    # Extract valid values
                    values = []
                    for data_point in market_data:
                        value = data_point.get(metric_type, 0.0)
                        if value is not None and value > 0:
                            try:
                                values.append(float(value))
                            except (ValueError, TypeError):
                                continue
                    
                    if len(values) < self.min_data_points:
                        continue

                    # Calculate statistics
                    mean = statistics.mean(values)
                    stdev = statistics.stdev(values) if len(values) > 1 else 0
                    
                    if stdev == 0:
                        continue
                    
                    # Define thresholds
                    upper_threshold = mean + self.anomaly_threshold * stdev
                    lower_threshold = mean - self.anomaly_threshold * stdev

                    # Detect anomalies
                    for data_point in market_data:
                        try:
                            value = float(data_point.get(metric_type, 0.0))
                            if value > 0:
                                if value > upper_threshold or value < lower_threshold:
                                    anomaly = {
                                        "type": "market_anomaly",
                                        "symbol": data_point.get("symbol", "unknown"),
                                        "metric_type": metric_type,
                                        "value": value,
                                        "mean": mean,
                                        "stdev": stdev,
                                        "upper_threshold": upper_threshold,
                                        "lower_threshold": lower_threshold,
                                        "severity": "high" if abs(value - mean) > 3 * stdev else "medium",
                                        "timestamp": int(time.time()),
                                        "description": f"Market anomaly in {metric_type} for {data_point.get('symbol')}: {value:.4f}"
                                    }
                                    anomalies.append(anomaly)
                                    self.logger.log_anomaly("market_anomaly", anomaly)
                        except (ValueError, TypeError) as e:
                            self.logger.log_error(f"Error processing market data value: {e}", {"data_point": data_point})
                            continue

                except Exception as e:
                    self.logger.log_error(f"Error processing market metric type {metric_type}: {e}")
                    continue

            return anomalies

        except Exception as e:
            self.logger.log_error(f"Error detecting market anomalies: {e}")
            return []

    async def detect_trend_anomalies(self, time_series_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in time series data using trend analysis."""
        try:
            if not time_series_data or len(time_series_data) < self.min_data_points:
                return []

            anomalies = []
            
            # Convert to DataFrame for easier analysis
            df = pd.DataFrame(time_series_data)
            
            # Sort by timestamp if available
            if 'timestamp' in df.columns:
                df = df.sort_values('timestamp')
            
            # Analyze each numeric column
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            for column in numeric_columns:
                if column == 'timestamp':
                    continue
                    
                try:
                    values = df[column].dropna().values
                    if len(values) < self.min_data_points:
                        continue
                    
                    # Calculate rolling statistics
                    window_size = min(10, len(values) // 2)
                    if window_size < 3:
                        continue
                    
                    rolling_mean = pd.Series(values).rolling(window=window_size).mean()
                    rolling_std = pd.Series(values).rolling(window=window_size).std()
                    
                    # Detect points that deviate significantly from rolling mean
                    for i in range(window_size, len(values)):
                        if not np.isnan(rolling_mean.iloc[i]) and not np.isnan(rolling_std.iloc[i]):
                            current_value = values[i]
                            expected_value = rolling_mean.iloc[i]
                            expected_std = rolling_std.iloc[i]
                            
                            if expected_std > 0:
                                z_score = abs(current_value - expected_value) / expected_std
                                
                                if z_score > self.anomaly_threshold:
                                    anomaly = {
                                        "type": "trend_anomaly",
                                        "metric": column,
                                        "value": current_value,
                                        "expected_value": expected_value,
                                        "z_score": z_score,
                                        "position": i,
                                        "severity": "high" if z_score > 3 else "medium",
                                        "timestamp": int(time.time()),
                                        "description": f"Trend anomaly in {column}: {current_value:.4f} (expected: {expected_value:.4f}, z-score: {z_score:.2f})"
                                    }
                                    anomalies.append(anomaly)
                                    self.logger.log_anomaly("trend_anomaly", anomaly)
                
                except Exception as e:
                    self.logger.log_error(f"Error analyzing trend for column {column}: {e}")
                    continue

            return anomalies

        except Exception as e:
            self.logger.log_error(f"Error detecting trend anomalies: {e}")
            return []

    async def get_anomaly_insights(self, anomalies: List[Dict[str, Any]]) -> List[str]:
        """Generate insights from anomaly detection."""
        try:
            insights = []
            
            if not anomalies:
                return insights
            
            # Group anomalies by type
            agent_anomalies = [a for a in anomalies if a.get("type") == "agent_anomaly"]
            market_anomalies = [a for a in anomalies if a.get("type") == "market_anomaly"]
            trend_anomalies = [a for a in anomalies if a.get("type") == "trend_anomaly"]
            
            # Agent performance insights
            if agent_anomalies:
                high_severity = [a for a in agent_anomalies if a.get("severity") == "high"]
                if high_severity:
                    insights.append(f"Found {len(high_severity)} high-severity agent performance anomalies requiring immediate attention")
                
                # Most common anomaly types
                metric_counts = {}
                for anomaly in agent_anomalies:
                    metric_type = anomaly.get("metric_type", "unknown")
                    metric_counts[metric_type] = metric_counts.get(metric_type, 0) + 1
                
                if metric_counts:
                    most_common = max(metric_counts.items(), key=lambda x: x[1])
                    insights.append(f"Most common anomaly type: {most_common[0]} ({most_common[1]} occurrences)")
            
            # Market insights
            if market_anomalies:
                insights.append(f"Detected {len(market_anomalies)} market anomalies that may indicate unusual market conditions")
                
                # Analyze by symbol
                symbol_counts = {}
                for anomaly in market_anomalies:
                    symbol = anomaly.get("symbol", "unknown")
                    symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
                
                if symbol_counts:
                    most_affected = max(symbol_counts.items(), key=lambda x: x[1])
                    insights.append(f"Most affected symbol: {most_affected[0]} ({most_affected[1]} anomalies)")
            
            # Trend insights
            if trend_anomalies:
                insights.append(f"Detected {len(trend_anomalies)} trend anomalies indicating potential regime changes")
            
            return insights

        except Exception as e:
            self.logger.log_error(f"Error generating anomaly insights: {e}")
            return []

    async def notify_core(self, result: Dict[str, Any]):
        """Notify Core Agent of anomaly detections."""
        try:
            self.logger.log_info(f"Notifying Core Agent: {result.get('description', 'unknown')}")
            
            # Publish to Redis for Core Agent
            notification = {
                "type": "anomaly_detection",
                "data": result,
                "timestamp": time.time(),
                "source": "intelligence_anomaly_detector"
            }
            
            # This would be implemented with Redis pub/sub
            # self.redis_client.publish("core:notifications", str(notification))
            
        except Exception as e:
            self.logger.log_error(f"Error in notify_core: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get anomaly detector statistics."""
        uptime = time.time() - self.stats["start_time"]
        
        return {
            "uptime_seconds": uptime,
            "total_detections": self.stats["total_detections"],
            "anomalies_found": self.stats["anomalies_found"],
            "detections_per_hour": self.stats["total_detections"] / max(uptime / 3600, 1),
            "last_detection_time": self.stats["last_detection_time"],
            "anomaly_threshold": self.anomaly_threshold,
            "min_data_points": self.min_data_points
        }