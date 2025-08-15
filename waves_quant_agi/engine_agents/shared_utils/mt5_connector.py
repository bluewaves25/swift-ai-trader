#!/usr/bin/env python3
"""
MT5 Connector - Centralized MetaTrader5 connection handler
Automatically detects and uses real MT5 when available, falls back to mock when needed
"""

import time
from typing import Optional, Dict, Any, List

# Global flag to track MT5 mode
MT5_MOCK_MODE = False

def get_mt5_module():
    """Get MT5 module - real if available, mock if not."""
    global MT5_MOCK_MODE
    
    try:
        # Try to import real MetaTrader5 first
        import MetaTrader5 as mt5
        MT5_MOCK_MODE = False
        print("🎯 REAL MT5: Successfully loaded MetaTrader5 module - will connect to your desktop app")
        return mt5
    except ImportError:
        # Import mock MT5 if real not available
        try:
            from .mt5_mock import MockMT5
            mt5 = MockMT5()
            MT5_MOCK_MODE = True
            print("🎭 MOCK MT5: Real MetaTrader5 not available - using simulation mode")
            return mt5
        except ImportError:
            # Create minimal inline mock
            MT5_MOCK_MODE = True
            print("⚠️ MINIMAL MOCK: Creating basic MT5 simulation")
            return create_minimal_mt5_mock()

def is_mock_mode() -> bool:
    """Check if running in mock mode."""
    return MT5_MOCK_MODE

def create_minimal_mt5_mock():
    """Create minimal MT5 mock for fallback."""
    class MinimalMT5Mock:
        def initialize(self, path="", login=0, password="", server="", timeout=60000, portable=False):
            return True
        
        def login(self, login=0, password="", server="", timeout=60000):
            return True
        
        def shutdown(self):
            pass
        
        def account_info(self):
            return type('AccountInfo', (), {
                'login': 248746257,
                'server': 'Mock-Demo',
                'currency': 'USD',
                'balance': 10000.0,
                'equity': 10000.0,
                'profit': 0.0
            })()
        
        def symbol_info_tick(self, symbol):
            return type('TickInfo', (), {
                'time': int(time.time()),
                'bid': 1.0850,
                'ask': 1.0852,
                'last': 1.0851,
                'volume': 1
            })()
        
        def symbols_get(self, group="*"):
            return [
                type('SymbolInfo', (), {'name': 'EURUSD'})(),
                type('SymbolInfo', (), {'name': 'GBPUSD'})(),
                type('SymbolInfo', (), {'name': 'USDJPY'})(),
            ]
        
        def symbol_select(self, symbol, enable=True):
            return True
        
        def positions_get(self, symbol=None, group="*", ticket=None):
            return []
        
        def orders_get(self, symbol=None, group="*", ticket=None):
            return []
        
        def order_send(self, request):
            return {
                'retcode': 10009,  # TRADE_RETCODE_DONE
                'deal': 123456,
                'order': 123456,
                'volume': request.get('volume', 0.01),
                'price': request.get('price', 1.0850),
                'comment': 'Mock order executed'
            }
        
        def last_error(self):
            return 0
        
        def version(self):
            return (500, 3550, "Mock MT5")
        
        # Constants
        TRADE_ACTION_DEAL = 1
        ORDER_TYPE_BUY = 0
        ORDER_TYPE_SELL = 1
        ORDER_FILLING_FOK = 0
        TIMEFRAME_M1 = 1
    
    return MinimalMT5Mock()

# Export the MT5 module for use by other components
mt5 = get_mt5_module()