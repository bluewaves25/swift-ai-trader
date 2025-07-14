# config/constants.py

from enum import Enum

class ModelMode(str, Enum):
    BACKTEST = "backtest"
    LIVE = "live"
    PAPER = "paper"

class AssetClass(str, Enum):
    FOREX = "forex"
    CRYPTO = "crypto"
    STOCKS = "stocks"
    COMMODITIES = "commodities"
    INDICES = "indices"

class BrokerType(str, Enum):
    BINANCE = "binance"
    METATRADER5 = "metatrader5"
    ALPACA = "alpaca"

class TradeSignal(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
