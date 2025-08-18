#!/usr/bin/env python3
"""Verify the position was opened correctly"""

import MetaTrader5 as mt5

if not mt5.initialize():
    print("❌ MT5 initialization failed")
    exit(1)

# Get positions for ETHUSDm
positions = mt5.positions_get(symbol="ETHUSDm")
if positions:
    print("✅ Position found:")
    for pos in positions:
        print(f"   Ticket: {pos.ticket}")
        print(f"   Symbol: {pos.symbol}")
        print(f"   Type: {'BUY' if pos.type == 0 else 'SELL'}")
        print(f"   Volume: {pos.volume}")
        print(f"   Price Open: {pos.price_open}")
        print(f"   Stop Loss: {pos.sl}")
        print(f"   Take Profit: {pos.tp}")
        print(f"   Profit: {pos.profit}")
        print(f"   Swap: {pos.swap}")
else:
    print("❌ No positions found for ETHUSDm")

mt5.shutdown()
