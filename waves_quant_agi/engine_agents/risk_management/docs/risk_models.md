# Risk Models

The `risk_management/` module employs advanced risk models to quantify and mitigate risks in trading.

## Traditional Risk Models

### Value at Risk (VaR)
- Measures potential loss in portfolio value over a specific time horizon at a given confidence level
- Calculated using historical simulation and Monte Carlo methods
- Example: 95% VaR of $100,000 indicates a 5% chance of losing more than $100,000 in a day

### Conditional Value at Risk (CVaR)
- Estimates expected loss in the worst-case scenarios beyond VaR
- Provides a more comprehensive risk assessment for tail events
- Used to set capital buffers for extreme market conditions

### Entropy-Based Uncertainty Model
- Quantifies uncertainty in market dynamics using information entropy
- High entropy triggers conservative strategies via the GracefulFallbackEngine
- Computed using quantum-inspired Monte Carlo simulations for speed

## NEW: Portfolio-Level Risk Models

### Daily Loss Limit Model (≤2%)
- **Purpose**: Prevents catastrophic daily portfolio losses
- **Method**: Real-time P&L tracking with rolling 24-hour window
- **Activation**: Circuit breaker triggers at 2% daily loss
- **Recovery**: Automatic reset at start of new day
- **Formula**: `Daily Loss % = (Current Value - Start Value) / Start Value * 100`

### Weekly Reward Target Model (≥20%)
- **Purpose**: Tracks progress toward weekly performance goals
- **Method**: 7-day rolling performance calculation
- **Target**: 20% weekly return on portfolio
- **Monitoring**: Continuous progress tracking with achievement notifications
- **Formula**: `Weekly Return % = (Current Value - Week Start Value) / Week Start Value * 100`

### Trailing Stop Loss Model
- **Purpose**: Dynamic profit protection for eligible strategies
- **Strategies**: trend_following, htf
- **Activation**: After profit threshold reached
- **Adjustment**: Automatic tightening as profits increase
- **Execution**: Immediate position closure on stop trigger

#### Trend Following Strategy
- **Trailing Distance**: 0.5%
- **Activation Threshold**: 1% profit
- **Tightening Increment**: 0.2%
- **Risk Profile**: Conservative profit locking

#### HTF Strategy
- **Trailing Distance**: 1.0%
- **Activation Threshold**: 1.5% profit
- **Tightening Increment**: 0.5%
- **Risk Profile**: Aggressive profit protection

## NEW: Circuit Breaker Models

### Daily Loss Circuit Breaker
- **Trigger Condition**: Daily portfolio loss > 2%
- **Action**: Immediate trading suspension
- **Recovery**: 24-hour timeout or manual override
- **Notification**: Publishes to execution_agent for position closure

### Performance Alert System
- **Warning Level**: 1.5% daily loss (75% of limit)
- **Breach Level**: 2.0% daily loss (100% of limit)
- **Response**: Escalating alerts and automatic actions

## NEW: Dynamic Risk Adjustment Models

### Volatility-Based Adjustment
- **Input**: Real-time market volatility data
- **Output**: Adjusted position sizes and stop distances
- **Method**: Volatility ratio analysis with historical comparison

### Liquidity-Based Adjustment
- **Input**: Market liquidity scores
- **Output**: Modified risk limits for illiquid assets
- **Method**: Liquidity threshold analysis with correlation factors

### Correlation-Based Adjustment
- **Input**: Portfolio correlation matrix
- **Output**: Diversified position sizing
- **Method**: Correlation threshold enforcement (max 0.7)

## Implementation

### Core Integration
- Models integrate with `quantum_risk_core/` for parallel processing
- **NEW**: Integrated with `PortfolioPerformanceTracker` for daily/weekly monitoring
- **NEW**: Integrated with `TrailingStopManager` for dynamic stop management
- **NEW**: Integrated with `StreamlinedRiskManager` for unified risk control

### Configuration
- Configurable thresholds ensure adaptability across market conditions
- **NEW**: Portfolio performance thresholds configurable via `PORTFOLIO_PERFORMANCE_CONFIG`
- **NEW**: Strategy-specific trailing stop parameters in `STRATEGY_RISK_LIMITS`
- **NEW**: Circuit breaker settings in `PERFORMANCE_THRESHOLDS`

### Data Storage & Logging
- Results stored in Redis with appropriate TTL (1 hour to 7 days)
- **NEW**: Performance history stored with 1000-entry rolling window
- **NEW**: Circuit breaker events logged with full context
- **NEW**: Trailing stop actions logged for audit trail
- All interactions logged via `FailureAgentLogger` for transparency

### Performance Characteristics
- **Real-time Processing**: Sub-second risk assessment
- **Scalability**: Linear scaling with number of positions
- **Reliability**: Circuit breaker protection prevents system overload
- **Adaptability**: Dynamic adjustment based on market conditions
