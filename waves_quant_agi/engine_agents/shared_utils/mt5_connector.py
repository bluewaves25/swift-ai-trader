#!/usr/bin/env python3
"""
MT5 Connector - REAL MetaTrader5 connection handler
Connects directly to your MT5 desktop application for REAL TRADING
"""

import MetaTrader5 as mt5

print("🎯 REAL MT5 TRADING: Connecting to your MetaTrader5 desktop application")
print("🎯 NO MOCKING - ALL TRADES WILL BE REAL!")

def is_mock_mode() -> bool:
    """Always returns False - we're using REAL MT5 only."""
    return False

def get_mt5_module():
    """Get REAL MT5 module only."""
    return mt5
