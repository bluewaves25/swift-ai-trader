# Risk Management Architecture Overview

The `risk_management/` module of Waves Quant acts as a "neural shield," protecting trading operations across Forex, Crypto, Indices, and Commodities. It integrates high-frequency trading (HFT), quantum-parallel inference, and continuous learning to ensure robust risk control.

## Core Components

### Strategy-Specific Risk Control
- Tailors risk logic to strategies like arbitrage, trend-following, and market-making
- **NEW**: Trailing stop loss management for trend_following and htf strategies
- **NEW**: Portfolio-level daily loss limit enforcement (≤2%)
- **NEW**: Weekly reward target tracking (≥20%)

### Portfolio Performance Tracking
- **NEW**: Real-time daily P&L monitoring with 2% loss limit
- **NEW**: Weekly performance tracking toward 20% reward target
- **NEW**: Circuit breaker system for automatic trading suspension on daily loss breach
- **NEW**: Daily and weekly tracking with automatic resets

### Trailing Stop Management
- **NEW**: Dynamic trailing stop loss for eligible strategies
- **Trend Following**: 0.5% trailing distance, activates at 1% profit
- **HTF**: 1% trailing distance, activates at 1.5% profit
- Automatic stop tightening as profits increase
- Immediate position closure on stop trigger

### Simulation Engine
- Runs stress tests and scenarios to evaluate risk under adverse conditions
- **NEW**: Integrated with daily loss limit testing
- **NEW**: Weekly reward target validation scenarios

### Audit Trails
- Ensures transparency with visual traces and redundancy checks
- **NEW**: Comprehensive performance history tracking
- **NEW**: Circuit breaker event logging

### Quantum Risk Core
- Uses quantum-inspired models for entropy and outcome evaluation
- **NEW**: Enhanced with portfolio-level risk assessment

### Learning Layer
- Continuously improves risk models via internal and external data analysis
- **NEW**: Performance pattern recognition for reward optimization

## Integration

- Communicates with Market Conditions, Executions, and Fee Monitor agents via Redis
- **NEW**: Publishes circuit breaker alerts to execution agent
- **NEW**: Real-time portfolio performance updates
- Supports trading in EUR/USD, USD/JPY, BTC, ETH, SOL, US 30, NAS 100, S&P 500, Gold, Silver, and Oil

## Design Principles

- Modularity for scalability
- Real-time risk assessment for HFT
- **NEW**: Automated risk management with zero manual intervention
- **NEW**: Circuit breaker protection for catastrophic loss prevention
- **NEW**: Profit protection through intelligent trailing stops
- Continuous learning for adaptive risk management
- Transparency through comprehensive logging and visualization

## New Risk Management Features

### Daily Loss Limit (≤2%)
- Portfolio value monitored continuously
- Automatic trading suspension when daily loss exceeds 2%
- Circuit breaker resets at start of new day
- Real-time alerts and notifications

### Trailing Stop Loss
- Automatic setup for trend_following and htf strategies
- Dynamic adjustment based on profit movement
- Configurable activation thresholds and tightening increments
- Immediate execution on stop trigger

### Weekly Reward Target (≥20%)
- 7-day rolling performance tracking
- Progress monitoring toward 20% weekly goal
- Achievement notifications and celebrations
- Weekly reset for continuous goal setting

## Architecture Benefits

1. **Risk Protection**: Automatic 2% daily loss limit prevents catastrophic losses
2. **Profit Locking**: Trailing stops lock in profits on winning trades
3. **Performance Goals**: Clear 20% weekly target provides motivation
4. **Automation**: No manual intervention required for risk management
5. **Real-time**: Continuous monitoring and immediate action on breaches
6. **Scalability**: Modular design supports multiple strategies and assets
7. **Transparency**: Comprehensive logging and performance tracking
