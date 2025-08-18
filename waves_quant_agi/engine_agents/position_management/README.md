# Position Management & Portfolio Optimization System

## 🎯 Overview

The Position Management & Portfolio Optimization System is a comprehensive solution that provides enterprise-level position tracking, risk management, and portfolio optimization for your AI trading engine. This system integrates seamlessly with your existing pipeline and provides advanced features for professional trading operations.

## 🚀 Features

### **Position Management**
- **Real-time Position Tracking**: Monitor all open positions with live PnL updates
- **Position Lifecycle Management**: Complete audit trail from entry to exit
- **Strategy Attribution**: Track which strategy generated each position
- **Performance Metrics**: Calculate risk-adjusted returns, drawdown, and time analysis

### **Portfolio Optimization**
- **Multi-Strategy Optimization**: Risk Parity, Mean-Variance, and Sharpe Ratio approaches
- **Dynamic Allocation**: Automatically adjust strategy allocations based on performance
- **Rebalancing Recommendations**: Actionable insights for portfolio improvement
- **Consensus Analysis**: Combine multiple optimization strategies for robust decisions

### **Advanced Risk Management**
- **Trailing Stops**: Strategy-specific trailing stop configurations
- **Partial Profit Taking**: Structured exit schedules at multiple profit levels
- **Dynamic SL/TP**: Real-time adjustments based on market conditions
- **Risk Coordination**: Unified risk management across all strategies

## 🏗️ Architecture

```
Position Management Coordinator
├── Position Manager
│   ├── Position Lifecycle
│   ├── Portfolio Metrics
│   └── Rebalancing Engine
├── Portfolio Optimizer
│   ├── Risk Parity
│   ├── Mean-Variance
│   └── Sharpe Ratio
└── Advanced Risk Coordinator
    ├── Trailing Stops
    ├── Partial Profits
    └── Dynamic SL/TP
```

## 📊 Strategy Allocations

| Strategy Type | Target | Min | Max | Rebalance Threshold |
|---------------|--------|-----|-----|---------------------|
| **Arbitrage (HFT)** | 25% | 15% | 35% | 5% |
| **Trend Following** | 20% | 10% | 30% | 5% |
| **Market Making** | 15% | 5% | 25% | 5% |
| **HTF** | 15% | 5% | 25% | 5% |
| **News Driven** | 15% | 5% | 25% | 5% |
| **Statistical Arbitrage** | 10% | 5% | 20% | 5% |

## 🔧 Configuration

### **Position Management Settings**
```python
config = {
    "position_management_update_frequency": 1.0,      # 1 second updates
    "portfolio_optimization_frequency": 300.0,        # 5 minutes
    "risk_update_frequency": 0.5,                    # 500ms updates
    "max_positions_per_strategy": 5,                 # Max positions per strategy
    "risk_allocation_per_strategy": 0.15             # 15% risk per strategy
}
```

### **Risk Management Parameters**
```python
# Trailing Stop Configuration
trailing_config = {
    "arbitrage": {
        "trailing_enabled": True,
        "trailing_distance": 0.002,      # 0.2% for HFT
        "activation_threshold": 0.005,   # Activate at 0.5% profit
        "max_trailing_distance": 0.01    # Max 1% trailing
    }
}

# Partial Profit Taking
partial_config = {
    "arbitrage": {
        "exit_levels": [
            {"profit_target": 0.005, "exit_percentage": 0.25, "sl_adjustment": 0.002},
            {"profit_target": 0.008, "exit_percentage": 0.25, "sl_adjustment": 0.003},
            {"profit_target": 0.012, "exit_percentage": 0.25, "sl_adjustment": 0.005},
            {"profit_target": 0.015, "exit_percentage": 0.25, "sl_adjustment": 0.008}
        ]
    }
}
```

## 📈 Usage Examples

### **Adding a Position**
```python
from engine_agents.position_management.position_management_coordinator import PositionManagementCoordinator

coordinator = PositionManagementCoordinator(config, logger)

position_data = {
    "position_id": "pos_001",
    "symbol": "EURUSD",
    "strategy_type": "arbitrage",
    "strategy_name": "Triangular Arbitrage",
    "action": "BUY",
    "volume": 0.1,
    "entry_price": 1.0850,
    "stop_loss": 1.0800,
    "take_profit": 1.0900
}

position_id = await coordinator.add_position(position_data)
```

### **Getting Portfolio Summary**
```python
portfolio_summary = await coordinator.get_coordinator_status()
print(f"Active Positions: {portfolio_summary['portfolio_summary']['active_positions']}")
print(f"Total PnL: {portfolio_summary['portfolio_summary']['portfolio_metrics']['total_pnl']}")
```

### **Portfolio Optimization**
```python
from engine_agents.position_management.portfolio_optimizer import PortfolioOptimizer

optimizer = PortfolioOptimizer(config, logger)

optimization_result = await optimizer.optimize_portfolio(portfolio_data, market_data)
recommendations = optimization_result['recommendations']

for rec in recommendations:
    print(f"Strategy: {rec['strategy_type']}")
    print(f"Action: {rec['action']}")
    print(f"Target Allocation: {rec['target_allocation']:.1%}")
    print(f"Priority: {rec['priority']}")
```

## 🔍 Monitoring & API Endpoints

### **Risk Management Status**
```bash
GET /api/risk-management/status
```
Returns comprehensive risk management status including:
- Active positions
- Trailing stop status
- Partial profit tracking
- Dynamic SL/TP adjustments

### **Portfolio Summary**
```bash
GET /api/position-management/portfolio-summary
```
Returns portfolio performance metrics:
- Strategy allocations
- PnL breakdown
- Rebalancing recommendations
- Risk exposure

### **Optimization Results**
```bash
GET /api/position-management/optimization-results
```
Returns latest portfolio optimization:
- Strategy recommendations
- Allocation targets
- Implementation plans
- Expected impact

## 🧪 Testing

Run the integration test to verify all components are working:

```bash
cd waves_quant_agi
python test_position_management_integration.py
```

This test verifies:
- Component initialization
- Position lifecycle management
- Portfolio optimization
- Risk management integration
- System coordination

## 🚨 Risk Management Rules

### **Daily Limits**
- **Maximum Daily Loss**: -2% of portfolio
- **Maximum Position Size**: 15% of portfolio
- **Maximum Correlation**: 70% between positions

### **Strategy-Specific Rules**
- **Arbitrage (HFT)**: Frequent small wins, 0.5% stop, 1% profit
- **Trend Following**: Fewer big wins, 3% stop, 6% profit
- **Market Making**: Moderate volatility, 2% stop, 4% profit

### **Profit Locking**
- **HFT Profits**: 50% to big trades, 30% to weekly target, 20% compound
- **Partial Exits**: Structured at 1:2, 1:3, 1:5 risk-reward ratios
- **Trailing Stops**: Activate at profit thresholds, trail for maximum gains

## 🔄 Integration with Main Pipeline

The Position Management System is automatically integrated into your main trading pipeline:

1. **Startup Order**: 8.5 (after risk management, before execution)
2. **Automatic Integration**: All positions are automatically tracked
3. **Real-time Updates**: Portfolio metrics update every second
4. **Risk Coordination**: Integrated with your existing risk management

## 📊 Performance Metrics

Monitor system performance through:

- **Positions Managed**: Total positions processed
- **Optimizations Performed**: Portfolio optimization count
- **Risk Events Processed**: Risk management events
- **Rebalancing Actions**: Portfolio rebalancing count

## 🎯 Next Steps

1. **Start Your Pipeline**: The system is automatically integrated
2. **Monitor Performance**: Check API endpoints for real-time status
3. **Review Recommendations**: Act on portfolio optimization suggestions
4. **Adjust Parameters**: Fine-tune risk management settings as needed

## 🆘 Troubleshooting

### **Common Issues**
- **Import Errors**: Ensure all dependencies are installed
- **Redis Connection**: Verify Redis is running and accessible
- **MT5 Connection**: Check MT5 credentials and connection status

### **Debug Mode**
Enable detailed logging by setting log level to DEBUG in your configuration.

---

**🎉 Your AI trading engine now has enterprise-level position management and portfolio optimization!**

The system will automatically:
- Track all positions with real-time PnL
- Optimize portfolio allocation across strategies
- Manage risk with advanced trailing stops and partial profits
- Provide actionable rebalancing recommendations
- Maintain your target 20% weekly growth with -2% daily risk limits
