#!/usr/bin/env python3
"""
Risk Management Configuration
Configuration file for the improved risk management system
"""

# Redis Configuration
REDIS_CONFIG = {
    'redis_host': 'localhost',
    'redis_port': 6379,
    'redis_db': 0
}

# Performance Thresholds
PERFORMANCE_THRESHOLDS = {
    'max_latency_ms': 100,           # Maximum allowed latency
    'min_throughput_per_sec': 1000,  # Minimum throughput requirement
    'max_error_rate': 0.01,          # Maximum error rate (1%)
    'min_cache_hit_rate': 0.9,       # Minimum cache hit rate (90%)
    'max_memory_usage_percent': 80,  # Maximum memory usage
    'max_cpu_usage_percent': 80,     # Maximum CPU usage
    'max_queue_size': 1000,          # Maximum queue size
    
    # USER REQUIREMENTS - Portfolio Risk Limits
    'max_daily_portfolio_loss': 0.02,    # 2% maximum daily portfolio loss
    'min_weekly_reward_target': 0.20,    # 20% minimum weekly reward target
    'portfolio_loss_circuit_breaker': True,  # Enable circuit breaker for daily loss
    'reward_optimization_enabled': True      # Enable weekly reward optimization
}

# Load Balancer Configuration
LOAD_BALANCER_CONFIG = {
    'num_workers': 4,                # Number of worker processes
    'max_queue_size': 1000,          # Maximum queue size per worker
    'routing_strategy': 'priority_based'  # Default routing strategy
}

# Circuit Breaker Configuration
CIRCUIT_BREAKER_CONFIG = {
    'risk_validation': {
        'failure_threshold': 5,       # Failures before opening circuit
        'recovery_timeout': 30        # Seconds to wait before testing recovery
    },
    'portfolio_monitoring': {
        'failure_threshold': 3,
        'recovery_timeout': 60
    },
    'data_fetching': {
        'failure_threshold': 10,
        'recovery_timeout': 120
    }
}

# Dynamic Risk Limits Configuration
DYNAMIC_RISK_LIMITS_CONFIG = {
    'cache_ttl': 300,                # Cache TTL in seconds (5 minutes)
    'max_cache_size': 1000,          # Maximum cache entries
    'volatility_threshold': 1.5,     # Volatility ratio threshold
    'liquidity_threshold': 0.5,      # Liquidity score threshold
    'correlation_threshold': 0.7     # Correlation threshold
}

# Performance Monitoring Configuration
PERFORMANCE_MONITOR_CONFIG = {
    'max_alerts': 1000,              # Maximum number of alerts to store
    'max_history': 10000,            # Maximum performance history entries
    'trend_analysis_window': 3600,   # Trend analysis window in seconds (1 hour)
    'performance_thresholds': PERFORMANCE_THRESHOLDS
}

# Adaptive Timer Configuration
ADAPTIVE_TIMER_CONFIG = {
    'fast_target_ms': 50,            # Target for fast validation (HFT)
    'comprehensive_target_ms': 500,  # Target for comprehensive validation
    'adjustment_factor': 0.1,        # Timing adjustment factor
    'max_adjustments': 100           # Maximum timing adjustments to store
}

# Strategy Risk Limits (Base values - will be dynamically adjusted)
STRATEGY_RISK_LIMITS = {
    'arbitrage': {
        'max_position_size': 0.05,    # 5% of portfolio
        'max_leverage': 2.0,          # 2x leverage
        'stop_loss': 0.002,           # 0.2% stop loss
        'max_drawdown': 0.01,         # 1% max drawdown
        'trailing_stop_enabled': False,  # No trailing stop for arbitrage
        'trailing_stop_distance': None
    },
    'trend_following': {
        'max_position_size': 0.15,    # 15% of portfolio
        'max_leverage': 1.2,          # 1.2x leverage
        'stop_loss': 0.01,            # 1% stop loss
        'max_drawdown': 0.03,         # 3% max drawdown
        'trailing_stop_enabled': True,   # USER REQUIREMENT: Trailing stop enabled
        'trailing_stop_distance': 0.005,  # 0.5% trailing stop distance
        'trailing_stop_activation': 0.01, # Activate after 1% profit
        'trailing_stop_tightening': 0.002 # Tighten by 0.2% increments
    },
    'market_making': {
        'max_position_size': 0.08,    # 8% of portfolio
        'max_leverage': 3.0,          # 3x leverage
        'stop_loss': 0.003,           # 0.3% stop loss
        'max_drawdown': 0.015,        # 1.5% max drawdown
        'trailing_stop_enabled': False,  # No trailing stop for market making
        'trailing_stop_distance': None
    },
    'news_driven': {
        'max_position_size': 0.12,    # 12% of portfolio
        'max_leverage': 1.0,          # No leverage
        'stop_loss': 0.008,           # 0.8% stop loss
        'max_drawdown': 0.025,        # 2.5% max drawdown
        'trailing_stop_enabled': False,  # No trailing stop for news driven
        'trailing_stop_distance': None
    },
    'htf': {
        'max_position_size': 0.20,    # 20% of portfolio
        'max_leverage': 1.0,          # No leverage
        'stop_loss': 0.02,            # 2% stop loss
        'max_drawdown': 0.05,         # 5% max drawdown
        'trailing_stop_enabled': True,    # USER REQUIREMENT: Trailing stop enabled
        'trailing_stop_distance': 0.01,   # 1% trailing stop distance
        'trailing_stop_activation': 0.015, # Activate after 1.5% profit
        'trailing_stop_tightening': 0.005  # Tighten by 0.5% increments
    }
}

# Safety Bounds for Risk Limits
SAFETY_BOUNDS = {
    'arbitrage': {
        'max_position_size': (0.02, 0.10),  # 2% to 10%
        'max_leverage': (1.0, 3.0),         # 1x to 3x
        'stop_loss': (0.001, 0.005),        # 0.1% to 0.5%
        'max_drawdown': (0.005, 0.02)       # 0.5% to 2%
    },
    'trend_following': {
        'max_position_size': (0.05, 0.25),  # 5% to 25%
        'max_leverage': (1.0, 2.0),         # 1x to 2x
        'stop_loss': (0.005, 0.02),         # 0.5% to 2%
        'max_drawdown': (0.01, 0.05)        # 1% to 5%
    },
    'market_making': {
        'max_position_size': (0.03, 0.15),  # 3% to 15%
        'max_leverage': (1.5, 4.0),         # 1.5x to 4x
        'stop_loss': (0.001, 0.008),        # 0.1% to 0.8%
        'max_drawdown': (0.005, 0.03)       # 0.5% to 3%
    },
    'news_driven': {
        'max_position_size': (0.05, 0.20),  # 5% to 20%
        'max_leverage': (1.0, 1.5),         # 1x to 1.5x
        'stop_loss': (0.005, 0.015),        # 0.5% to 1.5%
        'max_drawdown': (0.01, 0.04)        # 1% to 4%
    },
    'htf': {
        'max_position_size': (0.10, 0.30),  # 10% to 30%
        'max_leverage': (1.0, 1.5),         # 1x to 1.5x
        'stop_loss': (0.01, 0.03),          # 1% to 3%
        'max_drawdown': (0.02, 0.08)        # 2% to 8%
    }
}

# Portfolio Performance Tracking Configuration
PORTFOLIO_PERFORMANCE_CONFIG = {
    'daily_loss_limit': 0.02,         # 2% maximum daily portfolio loss
    'weekly_reward_target': 0.20,     # 20% minimum weekly reward target
    'performance_tracking_window': 7,  # 7 days for weekly calculations
    'daily_loss_circuit_breaker': True,  # Enable circuit breaker for daily loss
    'reward_optimization_enabled': True,  # Enable weekly reward optimization
    'trailing_stop_management': True,     # Enable trailing stop management
    'position_monitoring_interval': 60,   # Check positions every 60 seconds
    'performance_alert_threshold': 0.015  # Alert when daily loss > 1.5%
}

# Main Configuration
RISK_MANAGEMENT_CONFIG = {
    'redis': REDIS_CONFIG,
    'performance_thresholds': PERFORMANCE_THRESHOLDS,
    'load_balancer': LOAD_BALANCER_CONFIG,
    'circuit_breaker': CIRCUIT_BREAKER_CONFIG,
    'dynamic_risk_limits': DYNAMIC_RISK_LIMITS_CONFIG,
    'performance_monitor': PERFORMANCE_MONITOR_CONFIG,
    'adaptive_timer': ADAPTIVE_TIMER_CONFIG,
    'strategy_risk_limits': STRATEGY_RISK_LIMITS,
    'safety_bounds': SAFETY_BOUNDS,
    'portfolio_performance': PORTFOLIO_PERFORMANCE_CONFIG,  # Added portfolio performance config
    'num_workers': 4,
    'max_queue_size': 1000
}

# Environment-specific configurations
def get_config(environment: str = 'development') -> dict:
    """Get configuration for specific environment."""
    config = RISK_MANAGEMENT_CONFIG.copy()
    
    if environment == 'production':
        # Production overrides
        config['redis']['redis_host'] = 'redis.production.com'
        config['load_balancer']['num_workers'] = 8
        config['performance_thresholds']['max_latency_ms'] = 50
        config['performance_thresholds']['min_throughput_per_sec'] = 2000
        
    elif environment == 'staging':
        # Staging overrides
        config['redis']['redis_host'] = 'redis.staging.com'
        config['load_balancer']['num_workers'] = 6
        config['performance_thresholds']['max_latency_ms'] = 75
        
    elif environment == 'testing':
        # Testing overrides
        config['redis']['redis_host'] = 'localhost'
        config['load_balancer']['num_workers'] = 2
        config['performance_thresholds']['max_latency_ms'] = 200
    
    return config

# Default configuration
DEFAULT_CONFIG = get_config('development')
