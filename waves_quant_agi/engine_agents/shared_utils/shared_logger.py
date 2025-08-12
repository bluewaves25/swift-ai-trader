#!/usr/bin/env python3
"""
Shared Logger - ELIMINATE 90% OF LOGGING DUPLICATION
Single logging system for all agents to prevent massive code duplication

ELIMINATES DUPLICATION FROM:
- data_feeds/logs/data_feeds_logger.py
- strategy_engine/logs/strategy_logger.py  
- risk_management/logs/risk_logger.py
- market_conditions/logs/market_logger.py
- intelligence/logs/intelligence_logger.py
- execution/logs/execution_logger.py
- And 6+ other identical loggers across agents
"""

import logging
import time
import json
import os
from typing import Dict, Any, Optional, Union
from datetime import datetime
from logging.handlers import RotatingFileHandler
from .redis_connector import get_shared_redis

class SharedLogger:
    """
    Shared logger for all agents - eliminates massive logging code duplication.
    Provides file logging, Redis logging, and real-time monitoring.
    """
    
    def __init__(self, agent_name: str, component: str = "main", log_level: str = "INFO"):
        self.agent_name = agent_name
        self.component = component
        self.full_name = f"{agent_name}.{component}"
        
        # Get shared Redis connector
        try:
            self.redis_conn = get_shared_redis()
        except:
            self.redis_conn = None
        
        # Setup Python logger
        self.logger = logging.getLogger(self.full_name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_file_handler()
            self._setup_console_handler()
        
        # Log statistics
        self.stats = {
            "logs_written": 0,
            "errors_logged": 0,
            "warnings_logged": 0,
            "redis_logs_published": 0,
            "start_time": time.time()
        }
    
    def _setup_file_handler(self):
        """Setup file logging with rotation."""
        # Create logs directory structure
        log_dir = f"logs/{self.agent_name}"
        os.makedirs(log_dir, exist_ok=True)
        
        # Create rotating file handler
        log_file = os.path.join(log_dir, f"{self.component}.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # Set format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self):
        """Setup console logging for important messages."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
        
        formatter = logging.Formatter(
            '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def _publish_to_redis(self, level: str, message: str, metadata: Optional[Dict] = None):
        """Publish log to Redis for real-time monitoring."""
        if not self.redis_conn:
            return
        
        try:
            log_entry = {
                "timestamp": time.time(),
                "agent": self.agent_name,
                "component": self.component,
                "level": level.upper(),
                "message": message,
                "metadata": metadata or {}
            }
            
            # Publish to general log channel
            channel = f"logs:{self.agent_name}"
            self.redis_conn.publish(channel, log_entry)
            
            # Publish critical messages to alert channel
            if level.upper() in ["ERROR", "CRITICAL"]:
                alert_channel = "alerts:system"
                alert_entry = {
                    **log_entry,
                    "alert_type": "log_error",
                    "severity": level.upper()
                }
                self.redis_conn.publish(alert_channel, alert_entry)
            
            self.stats["redis_logs_published"] += 1
            
        except Exception as e:
            # Don't fail if Redis is unavailable
            pass
    
    def _log_with_stats(self, level: str, message: str, metadata: Optional[Dict] = None):
        """Internal method to log with statistics tracking."""
        # Update statistics
        self.stats["logs_written"] += 1
        if level.upper() == "ERROR":
            self.stats["errors_logged"] += 1
        elif level.upper() == "WARNING":
            self.stats["warnings_logged"] += 1
        
        # Add metadata to message if provided
        if metadata:
            message = f"{message} | Metadata: {json.dumps(metadata)}"
        
        # Log to file/console
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)
        
        # Publish to Redis
        self._publish_to_redis(level, message, metadata)
    
    # ============= PUBLIC LOGGING METHODS =============
    
    def info(self, message: str, metadata: Optional[Dict] = None):
        """Log info message."""
        self._log_with_stats("INFO", message, metadata)
    
    def debug(self, message: str, metadata: Optional[Dict] = None):
        """Log debug message."""
        self._log_with_stats("DEBUG", message, metadata)
    
    def warning(self, message: str, metadata: Optional[Dict] = None):
        """Log warning message."""
        self._log_with_stats("WARNING", message, metadata)
    
    def error(self, message: str, metadata: Optional[Dict] = None, exception: Optional[Exception] = None):
        """Log error message with optional exception."""
        if exception:
            message = f"{message} | Exception: {str(exception)}"
            if metadata is None:
                metadata = {}
            metadata["exception_type"] = type(exception).__name__
        
        self._log_with_stats("ERROR", message, metadata)
    
    def critical(self, message: str, metadata: Optional[Dict] = None):
        """Log critical message."""
        self._log_with_stats("CRITICAL", message, metadata)
    
    # ============= SPECIALIZED TRADING LOGGING =============
    
    def log_trade(self, trade_data: Dict[str, Any]):
        """Log trading activity."""
        message = f"TRADE: {trade_data.get('action', 'UNKNOWN')} {trade_data.get('quantity', 0)} {trade_data.get('symbol', 'UNKNOWN')} @ {trade_data.get('price', 0)}"
        self.info(message, {"trade_data": trade_data, "log_type": "trade"})
    
    def log_signal(self, signal_data: Dict[str, Any]):
        """Log trading signal."""
        message = f"SIGNAL: {signal_data.get('type', 'UNKNOWN')} for {signal_data.get('symbol', 'UNKNOWN')}"
        self.info(message, {"signal_data": signal_data, "log_type": "signal"})
    
    def log_performance(self, performance_data: Dict[str, Any]):
        """Log performance metrics."""
        message = f"PERFORMANCE: {json.dumps(performance_data)}"
        self.info(message, {"performance_data": performance_data, "log_type": "performance"})
    
    def log_market_data(self, symbol: str, price: float, volume: float):
        """Log market data update."""
        message = f"MARKET_DATA: {symbol} - Price: {price}, Volume: {volume}"
        self.debug(message, {"symbol": symbol, "price": price, "volume": volume, "log_type": "market_data"})
    
    def log_risk_event(self, risk_data: Dict[str, Any]):
        """Log risk management event."""
        severity = risk_data.get("severity", "info").lower()
        message = f"RISK_EVENT: {risk_data.get('event_type', 'UNKNOWN')} - {risk_data.get('description', 'No description')}"
        
        if severity == "critical":
            self.critical(message, {"risk_data": risk_data, "log_type": "risk"})
        elif severity == "warning":
            self.warning(message, {"risk_data": risk_data, "log_type": "risk"})
        else:
            self.info(message, {"risk_data": risk_data, "log_type": "risk"})
    
    def log_agent_status(self, status: str, details: Optional[Dict] = None):
        """Log agent status change."""
        message = f"AGENT_STATUS: {self.agent_name} - {status}"
        metadata = {"status": status, "log_type": "agent_status"}
        if details:
            metadata.update(details)
        
        if status.lower() in ["error", "failed", "stopped"]:
            self.error(message, metadata)
        elif status.lower() in ["warning", "degraded"]:
            self.warning(message, metadata)
        else:
            self.info(message, metadata)
    
    def log_execution_latency(self, operation: str, latency_ms: float, target_ms: float):
        """Log execution latency."""
        status = "OK" if latency_ms <= target_ms else "SLOW"
        message = f"LATENCY: {operation} - {latency_ms:.2f}ms (target: {target_ms}ms) - {status}"
        
        metadata = {
            "operation": operation,
            "latency_ms": latency_ms,
            "target_ms": target_ms,
            "status": status,
            "log_type": "latency"
        }
        
        if latency_ms > target_ms * 2:  # More than 2x target
            self.warning(message, metadata)
        else:
            self.debug(message, metadata)
    
    def log_communication(self, message_type: str, sender: str, receiver: str, success: bool):
        """Log inter-agent communication."""
        status = "SUCCESS" if success else "FAILED"
        message = f"COMM: {sender} -> {receiver} [{message_type}] - {status}"
        
        metadata = {
            "message_type": message_type,
            "sender": sender,
            "receiver": receiver,
            "success": success,
            "log_type": "communication"
        }
        
        if not success:
            self.warning(message, metadata)
        else:
            self.debug(message, metadata)
    
    # ============= UTILITY METHODS =============
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logging statistics."""
        uptime = time.time() - self.stats["start_time"]
        return {
            **self.stats,
            "uptime_seconds": uptime,
            "logs_per_second": self.stats["logs_written"] / max(uptime, 1),
            "error_rate": self.stats["errors_logged"] / max(self.stats["logs_written"], 1)
        }
    
    def flush(self):
        """Flush all log handlers."""
        for handler in self.logger.handlers:
            handler.flush()
    
    # Add missing methods that agents are calling
    def log_error(self, message: str):
        """Log error message (alias for error method)."""
        self.error(message)
    
    def log_metric(self, metric_name: str, value: Union[int, float], metadata: Optional[Dict] = None):
        """Log performance metric."""
        try:
            metric_data = {
                "metric": metric_name,
                "value": value,
                "timestamp": time.time(),
                "agent": self.agent_name,
                "component": self.component
            }
            if metadata:
                metric_data.update(metadata)
                
            self.info(f"METRIC: {metric_name}={value}")
            
        except Exception as e:
            self.error(f"Error logging metric: {e}")
    
    def log_optimization(self, optimization_type: str, details: Dict[str, Any]):
        """Log optimization event."""
        try:
            self.info(f"OPTIMIZATION: {optimization_type} - {details}")
        except Exception as e:
            self.error(f"Error logging optimization: {e}")
    
    def log_info(self, message: str):
        """Log info message (alias for info method)."""
        self.info(message)
    
    def set_level(self, level: str):
        """Change logging level."""
        self.logger.setLevel(getattr(logging, level.upper()))
    
    def close(self):
        """Close all handlers and cleanup."""
        for handler in self.logger.handlers:
            handler.close()
        self.logger.handlers.clear()

# ============= GLOBAL LOGGER MANAGEMENT =============

_agent_loggers: Dict[str, SharedLogger] = {}

def get_shared_logger(agent_name: str, component: str = "main", log_level: str = "INFO") -> SharedLogger:
    """Get or create a shared logger for an agent component."""
    logger_key = f"{agent_name}.{component}"
    
    if logger_key not in _agent_loggers:
        _agent_loggers[logger_key] = SharedLogger(agent_name, component, log_level)
    
    return _agent_loggers[logger_key]

def close_all_loggers():
    """Close all shared loggers."""
    for logger in _agent_loggers.values():
        logger.close()
    _agent_loggers.clear()

def get_all_logger_stats() -> Dict[str, Dict[str, Any]]:
    """Get statistics from all loggers."""
    stats = {}
    for logger_key, logger in _agent_loggers.items():
        stats[logger_key] = logger.get_stats()
    return stats

# ============= CONTEXT MANAGER FOR AUTOMATIC CLEANUP =============

class LoggingContext:
    """Context manager for automatic logger cleanup."""
    
    def __init__(self, agent_name: str, component: str = "main", log_level: str = "INFO"):
        self.agent_name = agent_name
        self.component = component
        self.log_level = log_level
        self.logger = None
    
    def __enter__(self) -> SharedLogger:
        self.logger = get_shared_logger(self.agent_name, self.component, self.log_level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.logger:
            self.logger.flush()

# Example usage
if __name__ == "__main__":
    def test_shared_logger():
        """Test the shared logger."""
        print("🧪 Testing Shared Logger...")
        
        # Test basic logging
        logger = get_shared_logger("test_agent", "main")
        
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message", {"error_code": 500})
        logger.debug("Test debug message")
        
        # Test specialized logging
        logger.log_trade({
            "action": "BUY",
            "symbol": "BTCUSD",
            "quantity": 0.1,
            "price": 30000
        })
        
        logger.log_signal({
            "type": "TREND_FOLLOWING",
            "symbol": "ETHUSD",
            "strength": 0.8
        })
        
        logger.log_execution_latency("order_placement", 50.5, 100.0)
        logger.log_execution_latency("slow_operation", 250.0, 100.0)
        
        logger.log_risk_event({
            "event_type": "DRAWDOWN_ALERT",
            "description": "Portfolio drawdown exceeded 5%",
            "severity": "warning"
        })
        
        # Test context manager
        with LoggingContext("context_agent", "test") as ctx_logger:
            ctx_logger.info("This is from context manager")
        
        # Get statistics
        stats = logger.get_stats()
        print(f"Logger stats: {stats}")
        
        all_stats = get_all_logger_stats()
        print(f"All logger stats: {all_stats}")
        
        print("✅ Shared Logger tests completed!")
        
        # Cleanup
        close_all_loggers()
    
    test_shared_logger()
