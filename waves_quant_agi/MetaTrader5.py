#!/usr/bin/env python3
"""
Mock MetaTrader5 module for Linux environment
Provides basic functionality to prevent import errors
"""

import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import IntEnum

# Mock enums and constants
class TRADE_ACTION(IntEnum):
    DEAL = 1
    PENDING = 5

class ORDER_TYPE(IntEnum):
    BUY = 0
    SELL = 1
    BUY_LIMIT = 2
    SELL_LIMIT = 3
    BUY_STOP = 4
    SELL_STOP = 5

class POSITION_TYPE(IntEnum):
    BUY = 0
    SELL = 1

class ORDER_FILLING_MODE(IntEnum):
    FILL_OR_KILL = 0
    IMMEDIATE_OR_CANCEL = 1
    RETURN = 2

class SYMBOL_MARGIN_MODE(IntEnum):
    FOREX = 0
    CFD = 1

# Mock data structures
@dataclass
class SymbolInfo:
    name: str = "EURUSD"
    bid: float = 1.0850
    ask: float = 1.0852
    point: float = 0.00001
    digits: int = 5
    spread: int = 2
    volume_min: float = 0.01
    volume_max: float = 500.0
    volume_step: float = 0.01
    margin_mode: int = SYMBOL_MARGIN_MODE.FOREX

@dataclass
class TickInfo:
    time: int = 0
    bid: float = 1.0850
    ask: float = 1.0852
    last: float = 1.0851
    volume: int = 1
    time_msc: int = 0
    flags: int = 0
    volume_real: float = 1.0

@dataclass
class TradePosition:
    ticket: int = 123456
    time: int = 0
    time_msc: int = 0
    time_update: int = 0
    time_update_msc: int = 0
    type: int = POSITION_TYPE.BUY
    magic: int = 0
    identifier: int = 123456
    reason: int = 0
    volume: float = 0.01
    price_open: float = 1.0850
    sl: float = 0.0
    tp: float = 0.0
    price_current: float = 1.0851
    swap: float = 0.0
    profit: float = 1.0
    symbol: str = "EURUSD"
    comment: str = "Mock position"
    external_id: str = ""

@dataclass
class TradeOrder:
    ticket: int = 123456
    time_setup: int = 0
    time_setup_msc: int = 0
    time_expiration: int = 0
    type: int = ORDER_TYPE.BUY_LIMIT
    type_filling: int = ORDER_FILLING_MODE.FILL_OR_KILL
    type_time: int = 0
    state: int = 0
    magic: int = 0
    position_id: int = 0
    position_by_id: int = 0
    reason: int = 0
    volume_initial: float = 0.01
    volume_current: float = 0.01
    price_open: float = 1.0850
    sl: float = 0.0
    tp: float = 0.0
    price_current: float = 1.0851
    price_stoplimit: float = 0.0
    symbol: str = "EURUSD"
    comment: str = "Mock order"
    external_id: str = ""

# Mock global variables
_connected = False
_account_info = {
    "login": 248746257,
    "server": "Mock-Demo",
    "currency": "USD",
    "balance": 10000.0,
    "equity": 10000.0,
    "profit": 0.0,
    "margin": 0.0,
    "margin_free": 10000.0,
    "margin_level": 0.0
}

# Mock functions
def initialize(path: str = "", login: int = 0, password: str = "", server: str = "", timeout: int = 60000, portable: bool = False) -> bool:
    """Mock initialize function."""
    global _connected
    print(f"Mock MT5: Initializing connection to {server} with login {login}")
    _connected = True
    return True

def login(login: int = 0, password: str = "", server: str = "", timeout: int = 60000) -> bool:
    """Mock login function."""
    global _connected
    print(f"Mock MT5: Logging in to {server} with login {login}")
    _connected = True
    return True

def shutdown() -> None:
    """Mock shutdown function."""
    global _connected
    print("Mock MT5: Shutting down connection")
    _connected = False

def terminal_info() -> Optional[Dict[str, Any]]:
    """Mock terminal info."""
    if not _connected:
        return None
    return {
        "community_account": False,
        "community_connection": False,
        "connected": True,
        "dlls_allowed": True,
        "trade_allowed": True,
        "tradeapi_disabled": False,
        "email_enabled": False,
        "ftp_enabled": False,
        "notifications_enabled": False,
        "mqid": False,
        "build": 3550,
        "maxbars": 65000,
        "codepage": 1252,
        "ping_last": 500,
        "community_balance": 0.0,
        "retransmission": 0.0,
        "company": "Mock Trading Company",
        "name": "Mock MetaTrader 5",
        "language": "English",
        "path": "/mock/path",
        "data_path": "/mock/data",
        "commondata_path": "/mock/common"
    }

def account_info() -> Optional[Dict[str, Any]]:
    """Mock account info."""
    if not _connected:
        return None
    return _account_info.copy()

def symbol_info(symbol: str) -> Optional[SymbolInfo]:
    """Mock symbol info."""
    if not _connected:
        return None
    return SymbolInfo(name=symbol)

def symbol_info_tick(symbol: str) -> Optional[TickInfo]:
    """Mock symbol tick info."""
    if not _connected:
        return None
    return TickInfo()

def symbol_select(symbol: str, enable: bool = True) -> bool:
    """Mock symbol select."""
    if not _connected:
        return False
    print(f"Mock MT5: {'Selecting' if enable else 'Deselecting'} symbol {symbol}")
    return True

def symbols_get(group: str = "*") -> Optional[List[SymbolInfo]]:
    """Mock symbols get."""
    if not _connected:
        return None
    
    # Return mock symbols
    symbols = [
        SymbolInfo(name="EURUSD"),
        SymbolInfo(name="GBPUSD"),
        SymbolInfo(name="USDJPY"),
        SymbolInfo(name="USDCHF"),
        SymbolInfo(name="AUDUSD"),
        SymbolInfo(name="USDCAD"),
        SymbolInfo(name="NZDUSD"),
    ]
    return symbols

def positions_get(symbol: str = None, group: str = "*", ticket: int = None) -> Optional[List[TradePosition]]:
    """Mock positions get."""
    if not _connected:
        return None
    
    # Return empty list for mock
    return []

def orders_get(symbol: str = None, group: str = "*", ticket: int = None) -> Optional[List[TradeOrder]]:
    """Mock orders get."""
    if not _connected:
        return None
    
    # Return empty list for mock
    return []

def order_send(request: Dict[str, Any]) -> Dict[str, Any]:
    """Mock order send."""
    if not _connected:
        return {"retcode": 10004, "comment": "No connection"}
    
    # Mock successful order
    return {
        "retcode": 10009,  # TRADE_RETCODE_DONE
        "deal": 123456,
        "order": 123456,
        "volume": request.get("volume", 0.01),
        "price": request.get("price", 1.0850),
        "bid": 1.0850,
        "ask": 1.0852,
        "comment": "Mock order executed",
        "request_id": 1,
        "retcode_external": 0
    }

def copy_rates_from_pos(symbol: str, timeframe: int, start_pos: int, count: int) -> Optional[List[Dict[str, Any]]]:
    """Mock copy rates."""
    if not _connected:
        return None
    
    # Return mock OHLC data
    base_time = int(time.time()) - (count * 60)  # 1-minute bars
    rates = []
    
    for i in range(count):
        bar_time = base_time + (i * 60)
        rates.append({
            "time": bar_time,
            "open": 1.0850 + (i * 0.0001),
            "high": 1.0855 + (i * 0.0001),
            "low": 1.0845 + (i * 0.0001),
            "close": 1.0851 + (i * 0.0001),
            "tick_volume": 100 + i,
            "spread": 2,
            "real_volume": 0
        })
    
    return rates

def copy_ticks_from(symbol: str, date_from: int, count: int, flags: int) -> Optional[List[Dict[str, Any]]]:
    """Mock copy ticks."""
    if not _connected:
        return None
    
    # Return mock tick data
    ticks = []
    base_time = int(time.time() * 1000)  # milliseconds
    
    for i in range(count):
        tick_time = base_time + (i * 1000)  # 1 second intervals
        ticks.append({
            "time": tick_time // 1000,
            "time_msc": tick_time,
            "bid": 1.0850 + (i * 0.00001),
            "ask": 1.0852 + (i * 0.00001),
            "last": 1.0851 + (i * 0.00001),
            "volume": 1,
            "volume_real": 1.0,
            "flags": flags
        })
    
    return ticks

def last_error() -> int:
    """Mock last error."""
    return 0  # No error

def version() -> tuple:
    """Mock version info."""
    return (500, 3550, "15 Dec 2023")

# Mock timeframe constants
TIMEFRAME_M1 = 1
TIMEFRAME_M5 = 5
TIMEFRAME_M15 = 15
TIMEFRAME_M30 = 30
TIMEFRAME_H1 = 16385
TIMEFRAME_H4 = 16388
TIMEFRAME_D1 = 16408
TIMEFRAME_W1 = 32769
TIMEFRAME_MN1 = 49153

# Mock error codes
RES_S_OK = 0
ERR_SUCCESS = 0
ERR_NO_CONNECTION = 4
ERR_NOT_ENOUGH_RIGHTS = 7
ERR_TOO_FREQUENT_REQUESTS = 8
ERR_MALFUNCTIONAL_TRADE = 9
ERR_ACCOUNT_DISABLED = 64
ERR_INVALID_ACCOUNT = 65

print("Mock MetaTrader5 module loaded successfully")