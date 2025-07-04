
import MetaTrader5 as mt5
import sys
import json
import pandas as pd
from datetime import datetime

def get_market_data(symbol):
    """Get market data for a specific symbol"""
    try:
        # Initialize MT5 connection
        if not mt5.initialize():
            return {"error": "MT5 initialization failed"}
        
        # Get symbol info
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            return {"error": f"Symbol {symbol} not found"}
        
        # Get current tick
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return {"error": f"Failed to get tick for {symbol}"}
        
        # Get recent rates (last 100 bars)
        rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 100)
        if rates is None or len(rates) == 0:
            return {"error": f"Failed to get rates for {symbol}"}
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Calculate technical indicators
        def calculate_rsi(prices, period=14):
            delta = prices.diff()
            gain = delta.where(delta > 0, 0).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1] if not rsi.empty else 50
        
        def calculate_bollinger_bands(prices, period=20, std_dev=2):
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            return upper_band.iloc[-1], lower_band.iloc[-1]
        
        def detect_market_condition(df):
            if len(df) < 20:
                return "ranging"
            
            # Simple trend detection
            recent_highs = df['high'].tail(10)
            recent_lows = df['low'].tail(10)
            
            if recent_highs.is_monotonic_increasing:
                return "trending_up"
            elif recent_lows.is_monotonic_decreasing:
                return "trending_down"
            elif (recent_highs.max() - recent_highs.min()) > (recent_highs.mean() * 0.01):
                return "volatile"
            else:
                return "ranging"
        
        # Calculate indicators
        rsi = calculate_rsi(df['close'])
        bollinger_upper, bollinger_lower = calculate_bollinger_bands(df['close'])
        market_condition = detect_market_condition(df)
        
        # Support and resistance levels (simplified)
        support_level = df['low'].tail(20).min()
        resistance_level = df['high'].tail(20).max()
        
        # MACD calculation (simplified)
        ema_12 = df['close'].ewm(span=12).mean()
        ema_26 = df['close'].ewm(span=26).mean()
        macd = ema_12.iloc[-1] - ema_26.iloc[-1] if len(df) > 26 else 0
        
        # Prepare response
        latest_rate = df.iloc[-1]
        
        market_data = {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "open_price": float(latest_rate['open']),
            "high_price": float(latest_rate['high']),
            "low_price": float(latest_rate['low']),
            "close_price": float(latest_rate['close']),
            "volume": int(latest_rate['tick_volume']),
            "spread": float(tick.ask - tick.bid),
            "bid": float(tick.bid),
            "ask": float(tick.ask),
            "market_condition": market_condition,
            "technical_indicators": {
                "rsi": float(rsi) if not pd.isna(rsi) else 50.0,
                "macd": float(macd) if not pd.isna(macd) else 0.0,
                "bollinger_upper": float(bollinger_upper) if not pd.isna(bollinger_upper) else float(latest_rate['close']) * 1.02,
                "bollinger_lower": float(bollinger_lower) if not pd.isna(bollinger_lower) else float(latest_rate['close']) * 0.98,
                "support_level": float(support_level),
                "resistance_level": float(resistance_level)
            },
            "volatility": float(df['close'].tail(20).std()) if len(df) >= 20 else 0.0
        }
        
        return market_data
        
    except Exception as e:
        return {"error": str(e)}
    
    finally:
        mt5.shutdown()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Symbol parameter required"}))
        sys.exit(1)
    
    symbol = sys.argv[1]
    result = get_market_data(symbol)
    print(json.dumps(result, default=str))
