# API Documentation

The `risk_management/` module provides APIs for integration with Waves Quant components.

## Core Risk Management Endpoints

### `/risk/evaluate`
Evaluates strategy-specific risks (e.g., MacroTrendTrackerRisk, RegimeShiftDetectorRisk).
- **Input**: JSON with strategy, symbol, data (e.g., trend strength, volatility)
- **Output**: JSON with decision, description, timestamp

### `/risk/stress_test`
Runs stress tests via StressTestRunner.
- **Input**: JSON with scenarios, symbols
- **Output**: JSON with results, visuals_path

### `/risk/entropy`
Computes entropy via QuantumMonteCarlo.
- **Input**: JSON with symbol, price_changes
- **Output**: JSON with entropy, description

### `/risk/retrain`
Triggers retraining via RetrainingLoop.
- **Input**: JSON with risk_type, incident_data
- **Output**: JSON with trigger_status, timestamp

## NEW: Portfolio Performance Management

### `/risk/portfolio/performance`
Updates and retrieves portfolio performance metrics.
- **Input**: JSON with portfolio data (total_value, positions, etc.)
- **Output**: JSON with daily/weekly P&L, loss limits, reward targets
- **Features**: 
  - Daily loss limit monitoring (≤2%)
  - Weekly reward target tracking (≥20%)
  - Circuit breaker status

### `/risk/portfolio/summary`
Gets comprehensive portfolio performance summary.
- **Input**: None (GET request)
- **Output**: JSON with current metrics, daily/weekly trackers, circuit breaker state
- **Features**: Performance history, drawdown analysis, achievement tracking

### `/risk/portfolio/reset`
Resets tracking data for daily/weekly performance.
- **Input**: JSON with tracking_type ('daily', 'weekly', 'all')
- **Output**: JSON with reset confirmation and new baseline values

## NEW: Trailing Stop Management

### `/risk/trailing_stop/initialize`
Initializes trailing stop for a new position.
- **Input**: JSON with position_id, strategy_type, entry_price, position_size, side
- **Output**: JSON with initialization status and trailing stop parameters
- **Supported Strategies**: trend_following, htf

### `/risk/trailing_stop/update`
Updates trailing stop based on current price.
- **Input**: JSON with position_id, current_price
- **Output**: JSON with stop action (if triggered) or update confirmation
- **Features**: Dynamic stop adjustment, profit locking, automatic execution

### `/risk/trailing_stop/summary`
Gets summary of all active trailing stops.
- **Input**: None (GET request)
- **Output**: JSON with total active, activated, pending activation counts

### `/risk/trailing_stop/close`
Closes trailing stop for a position.
- **Input**: JSON with position_id
- **Output**: JSON with closure confirmation

## NEW: Risk Validation & Management

### `/risk/validate_trade`
Validates trade request against risk limits.
- **Input**: JSON with trade_request (strategy, symbol, size, leverage, etc.)
- **Output**: JSON with approval status, risk assessment, conditions
- **Features**: Dynamic risk limits, strategy-specific validation, load balancing

### `/risk/manage_position`
Manages risk for an active position.
- **Input**: JSON with position_id, position_data (strategy_type, entry_price, etc.)
- **Output**: JSON with risk management status, trailing stop activation
- **Features**: Automatic trailing stop setup, position monitoring

### `/risk/update_prices`
Updates position prices and checks trailing stops.
- **Input**: JSON array with position updates (position_id, current_price)
- **Output**: JSON array with stop actions (if any triggered)
- **Features**: Real-time stop monitoring, automatic execution

## Integration

- APIs communicate via Redis channels:
  - `execution_agent`: For trade execution and circuit breaker actions
  - `risk_management_output`: For risk alerts and notifications
  - `risk_management_alerts`: For daily loss breach notifications
- Data stored with 1-hour to 7-day expiry based on context
- Secured with authentication tokens (configured in config)

## Usage

- Called by Executions and Market Conditions agents
- **NEW**: Integrated with portfolio performance monitoring
- **NEW**: Real-time trailing stop management
- **NEW**: Automatic circuit breaker activation
- Supports Forex, Crypto, Indices, and Commodities
- Logs interactions via FailureAgentLogger for auditability

## NEW: Circuit Breaker System

### Automatic Activation
- **Daily Loss Limit**: Triggers when portfolio daily loss > 2%
- **Action**: Suspends all trading, closes all positions
- **Recovery**: Resets at start of new day
- **Notification**: Publishes to execution_agent and risk_management_alerts

### Manual Override
- **Endpoint**: `/risk/circuit_breaker/reset`
- **Input**: JSON with override_reason, admin_token
- **Output**: JSON with reset confirmation and new status

## NEW: Performance Tracking

### Daily Tracking
- **Reset**: Automatic at midnight each day
- **Monitoring**: Real-time P&L calculation
- **Alerts**: Warning at 1.5% loss, breach at 2% loss
- **Storage**: 24-hour rolling window

### Weekly Tracking
- **Reset**: Automatic every 7 days
- **Target**: 20% weekly reward goal
- **Progress**: Continuous monitoring and notifications
- **Achievement**: Celebration and reset for new week
