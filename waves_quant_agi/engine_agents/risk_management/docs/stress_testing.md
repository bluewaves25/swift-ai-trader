# Stress Testing Design

The `simulation_engine/` within `risk_management/` conducts stress tests to evaluate portfolio resilience.

## Core Components

### StressTestRunner
- Executes historical and synthetic stress tests (e.g., market crashes, volatility spikes)
- **NEW**: Portfolio daily loss limit testing (2% breach scenarios)
- **NEW**: Weekly reward target validation (20% achievement scenarios)
- **NEW**: Trailing stop loss effectiveness testing

### ScenarioBuilder
- Generates adverse scenarios like black swans or liquidity drops
- **NEW**: Daily loss limit breach scenarios
- **NEW**: Trailing stop trigger scenarios
- **NEW**: Circuit breaker activation scenarios

### OutcomeVisualizer
- Visualizes test results for transparency
- **NEW**: Daily P&L tracking charts
- **NEW**: Weekly performance progress visualization
- **NEW**: Trailing stop activation and execution charts

### RecoveryAnalyzer
- Quantifies recovery times post-stress
- **NEW**: Circuit breaker recovery analysis
- **NEW**: Portfolio performance recovery metrics

## NEW: Risk Management Testing Scenarios

### Daily Loss Limit Testing
- **Scenario**: Portfolio value drops 2.5% in a single day
- **Expected Result**: Circuit breaker activates, trading suspended
- **Recovery Test**: System reset at start of new day
- **Validation**: All positions closed, no new trades allowed

### Trailing Stop Effectiveness Testing
- **Trend Following Strategy**:
  - **Scenario**: Price rises 2% then drops 1%
  - **Expected Result**: Trailing stop activates at 1% profit, locks in gains
  - **Validation**: Position closed at optimal profit level

- **HTF Strategy**:
  - **Scenario**: Price rises 3% then drops 1.5%
  - **Expected Result**: Trailing stop activates at 1.5% profit, aggressive protection
  - **Validation**: Higher profit threshold maintained

### Weekly Reward Target Testing
- **Scenario**: Portfolio achieves 22% weekly return
- **Expected Result**: Target achievement notification, celebration
- **Reset Test**: Weekly tracking resets for new week
- **Validation**: Continuous goal setting maintained

### Circuit Breaker Stress Testing
- **Rapid Loss Scenario**: 3% loss in 2 hours
- **Expected Result**: Immediate circuit breaker activation
- **Notification Test**: Execution agent receives close-all-positions command
- **Recovery Test**: Manual override capability validation

## Methodology

### Traditional Stress Tests
- Tests cover extreme market conditions across Forex, Crypto, Indices, and Commodities
- Scenarios simulate 10-20% price drops, 50% volatility spikes, and liquidity reductions
- Results stored in Redis with a 7-day expiry for analysis

### NEW: Risk Management Tests
- **Daily Loss Scenarios**: 1.5%, 2.0%, 2.5%, 3.0% daily losses
- **Trailing Stop Scenarios**: Various profit levels and price reversals
- **Weekly Performance Scenarios**: 15%, 20%, 25% weekly returns
- **Circuit Breaker Scenarios**: Multiple breach levels and recovery patterns

### Test Execution
- **Frequency**: Daily for critical risk management functions
- **Duration**: 24-hour cycles for daily loss testing
- **Coverage**: All supported strategies and asset classes
- **Validation**: Automated result verification and alerting

## Integration

### Market Conditions Integration
- Interacts with `market_conditions/` for real-time data
- **NEW**: Real-time portfolio value monitoring
- **NEW**: Continuous P&L calculation
- **NEW**: Market regime detection for risk adjustment

### Execution Agent Integration
- Notifies `execution_agent` for failed tests to adjust positions
- **NEW**: Circuit breaker activation notifications
- **NEW**: Trailing stop execution commands
- **NEW**: Portfolio-wide position closure orders

### Visualization and Reporting
- Visuals saved in `stress_test_visuals/` for stakeholder review
- **NEW**: Daily performance dashboards
- **NEW**: Weekly progress tracking charts
- **NEW**: Risk management effectiveness metrics

## NEW: Automated Testing Framework

### Continuous Monitoring
- **Real-time Validation**: Portfolio performance continuously monitored
- **Automatic Testing**: Daily loss scenarios tested automatically
- **Alert System**: Immediate notification of any test failures

### Performance Metrics
- **Circuit Breaker Response Time**: < 1 second activation
- **Trailing Stop Accuracy**: 95%+ profit protection
- **Daily Loss Prevention**: 100% breach prevention
- **Weekly Target Achievement**: 90%+ goal completion rate

### Test Results Storage
- **Performance History**: 1000-entry rolling window
- **Alert Logging**: All circuit breaker events logged
- **Recovery Analysis**: Post-breach performance tracking
- **Trend Analysis**: Long-term risk management effectiveness
