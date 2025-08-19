# Quick Reference Guide 🚀

## Strategy Engine + Risk Management Overview

### **System Architecture** 🏗️

```
Data Feeds → Strategy Engine → Risk Management → Execution
    ↓              ↓              ↓            ↓
Market Data → Signal Generation → Validation → Trade Execution
```

### **Key Components** 🧩

#### **Strategy Engine** 🎯
- **Signal Generation**: Creates trading signals
- **Strategy Management**: Manages multiple strategies
- **Learning System**: Improves performance over time
- **Optimization**: Automatically adjusts parameters

#### **Risk Management** 🛡️
- **Trade Validation**: Approves/rejects trades
- **Portfolio Monitoring**: Tracks exposure and risk
- **Position Management**: Manages individual positions
- **Circuit Breakers**: Emergency stop mechanisms

## Quick Configuration ⚙️

### **Strategy Engine Settings**
```python
strategy_config = {
    "max_active_strategies": 10,      # Max strategies running
    "min_signal_quality": 70,         # Minimum signal quality
    "max_risk_per_trade": 0.02,      # 2% risk per trade
    "learning_rate": 0.01,           # Learning speed
    "optimization_interval": 3600,    # Optimize every hour
}
```

### **Risk Management Settings**
```python
risk_config = {
    "max_risk_per_trade": 0.02,          # 2% risk per trade
    "max_portfolio_exposure": 0.80,      # 80% total exposure
    "max_single_asset": 0.20,            # 20% in single asset
    "stop_loss_percentage": 0.03,        # 3% stop loss
    "min_risk_reward": 2.0,              # 1:2 risk-reward ratio
    "circuit_breaker_threshold": 0.15,   # 15% daily loss limit
}
```

## Quick Start Checklist ✅

### **1. Setup (5 minutes)**
- [ ] Install required packages
- [ ] Configure basic settings
- [ ] Set up logging

### **2. Strategy Selection (10 minutes)**
- [ ] Choose 2-3 strategies to start
- [ ] Set basic parameters
- [ ] Configure risk limits

### **3. Initial Testing (15 minutes)**
- [ ] Run quick backtest
- [ ] Validate risk settings
- [ ] Check signal generation

### **4. Live Trading (5 minutes)**
- [ ] Start with small positions
- [ ] Monitor first trades
- [ ] Adjust if needed

## Common Commands 🖥️

### **Start Strategy Engine**
```python
from waves_quant_agi.engine_agents.strategy_engine import StrategyEnhancementManager

manager = StrategyEnhancementManager("strategy_engine", config)
await manager.start()
```

### **Start Risk Management**
```python
from waves_quant_agi.engine_agents.risk_management import EnhancedRiskManagementAgent

risk_manager = EnhancedRiskManagementAgent("risk_management", config)
await risk_manager.start()
```

### **Check System Status**
```python
# Strategy Engine Status
strategy_status = await manager.get_status()
print(f"Active Strategies: {strategy_status['active_strategies']}")

# Risk Management Status
risk_status = await risk_manager.get_status()
print(f"Portfolio Exposure: {risk_status['portfolio_exposure']}")
```

## Quick Troubleshooting 🔧

### **No Signals Generated?**
- Check signal quality threshold (lower from 70 to 50)
- Verify market data is flowing
- Check strategy parameters

### **Trades Being Rejected?**
- Review risk limits (increase if too strict)
- Check position sizing calculations
- Verify stop-loss levels

### **System Not Starting?**
- Check Redis connection
- Verify configuration files
- Check log files for errors

## Performance Metrics 📊

### **Strategy Engine Metrics**
- **Signal Quality**: Average signal score
- **Strategy Performance**: Individual strategy returns
- **Learning Progress**: Improvement over time
- **Optimization Results**: Parameter adjustments

### **Risk Management Metrics**
- **Portfolio Exposure**: Total position exposure
- **Risk Per Trade**: Individual trade risk
- **Drawdown**: Maximum portfolio decline
- **Sharpe Ratio**: Risk-adjusted returns

## Quick Tips 💡

### **Strategy Engine**
- Start with 2-3 simple strategies
- Use conservative parameters initially
- Enable learning gradually
- Monitor strategy performance daily

### **Risk Management**
- Begin with 1% risk per trade
- Set realistic portfolio limits
- Use ATR-based stop losses
- Monitor correlations

### **General**
- Test everything in backtest first
- Start with small position sizes
- Monitor system health regularly
- Keep logs for debugging

## Emergency Procedures 🚨

### **Circuit Breaker Triggered**
1. Check portfolio exposure
2. Review recent trades
3. Adjust risk parameters
4. Restart if necessary

### **System Crash**
1. Check error logs
2. Restart components
3. Verify connections
4. Check system resources

### **Excessive Losses**
1. Stop all trading
2. Review risk settings
3. Check strategy logic
4. Reduce position sizes

## Support Resources 📚

### **Documentation**
- `STRATEGY_ENGINE_COMPLETE_GUIDE.md` - Detailed Strategy Engine guide
- `RISK_MANAGEMENT_COMPLETE_GUIDE.md` - Detailed Risk Management guide
- `ROLE_VERIFICATION.md` - System architecture overview

### **Testing**
- `test_strategy_enhancements.py` - Strategy Engine tests
- `test_risk_management_cleanup.py` - Risk Management tests

### **Configuration**
- Check `__init__.py` files for import paths
- Review configuration dictionaries
- Verify environment variables

---

**Need Help?** Check the detailed guides first, then review logs, and finally check system status with the commands above.

**Happy Trading! 🎯📈**
