#!/usr/bin/env python3
"""
Live MT5 Execution Bridge - REAL TRADING EXECUTION
Connects strategy signals directly to live MT5 trading
"""

import asyncio
import time
import os
import MetaTrader5 as mt5
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from engine_agents.shared_utils import get_shared_logger, get_shared_redis

# Load environment variables from .env file
load_dotenv()

class LiveMT5ExecutionBridge:
    """
    Bridge that connects strategy signals to live MT5 trading.
    This replaces placeholder execution with REAL TRADES.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("execution", "mt5_bridge")
        self.redis_conn = get_shared_redis()
        self.is_connected = False
        
        # Get MT5 credentials from environment
        self.mt5_login = int(os.getenv("MT5_LOGIN", 0))
        self.mt5_password = os.getenv("MT5_PASSWORD", "")
        self.mt5_server = os.getenv("MT5_SERVER", "Exness-MT5Trial")
        
        # Demo mode flag
        self.demo_mode = self.mt5_login == 0 or not self.mt5_password
        
        # Execution settings
        self.lot_size = float(os.getenv("MT5_LOT_SIZE", "0.01"))  # Default micro lot
        self.max_slippage = 3  # Max slippage in points
        self.magic_number = 12345  # Unique identifier for our trades
        
        # Track active orders
        self.active_orders = {}
        
    async def connect(self):
        """Connect to live MT5 for trading."""
        if self.demo_mode:
            self.logger.info("📊 Demo Mode: Simulating live trading (no MT5 credentials)")
            self.is_connected = True
            return True
            
        try:
            if not mt5.initialize():
                self.logger.error("❌ MT5 initialize() failed")
                return False
                
            authorized = mt5.login(self.mt5_login, password=self.mt5_password, server=self.mt5_server)
            if not authorized:
                error_code = mt5.last_error()
                self.logger.error(f"❌ MT5 login failed: {error_code}")
                mt5.shutdown()
                return False
                
            self.is_connected = True
            account_info = mt5.account_info()
            if account_info:
                self.logger.info(f"✅ Connected to MT5 for LIVE TRADING - Account: {account_info.login}, Balance: {account_info.balance}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ MT5 connection error: {e}")
            return False
    
    async def execute_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a trading signal on live MT5.
        THIS IS WHERE YOUR STRATEGIES BECOME REAL TRADES!
        """
        if not self.is_connected:
            await self.connect()
            
        try:
            symbol = signal.get("symbol", "EURUSD")
            action = signal.get("action", "HOLD")
            strategy = signal.get("strategy", "unknown")
            confidence = signal.get("confidence", 0.5)
            
            # Skip HOLD signals
            if action == "HOLD":
                return {"status": "skipped", "reason": "HOLD signal"}
            
            # Validate minimum confidence
            if confidence < 0.6:
                return {"status": "skipped", "reason": f"Low confidence: {confidence}"}
            
            # Calculate lot size based on confidence and risk management
            adjusted_lot_size = self.lot_size * confidence
            
            if self.demo_mode:
                # DEMO MODE: Simulate trade execution
                import random
                order_id = random.randint(10000, 99999)
                simulated_price = 1.0850 if symbol == "EURUSD" else 1.2650  # Mock prices
                
                trade_info = {
                    "status": "executed",
                    "order_id": order_id,
                    "symbol": symbol,
                    "action": action,
                    "volume": adjusted_lot_size,
                    "price": simulated_price,
                    "strategy": strategy,
                    "confidence": confidence,
                    "timestamp": time.time(),
                    "demo_mode": True
                }
                
                # Store simulated order
                self.active_orders[order_id] = trade_info
                
                # Log simulated trade
                self.logger.info(f"📊 DEMO TRADE EXECUTED: {action} {adjusted_lot_size} {symbol} @ {simulated_price} (Strategy: {strategy})")
                
                return trade_info
            
            # LIVE MODE: Real MT5 execution
            # Determine order type
            order_type = mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL
            
            # Get current price
            tick = mt5.symbol_info_tick(symbol)
            if not tick:
                return {"status": "error", "reason": f"No price data for {symbol}"}
            
            price = tick.ask if action == "BUY" else tick.bid
            
            # Prepare order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": adjusted_lot_size,
                "type": order_type,
                "price": price,
                "sl": 0.0,  # Stop loss (0 = no stop loss)
                "tp": 0.0,  # Take profit (0 = no take profit)
                "deviation": self.max_slippage,
                "magic": self.magic_number,
                "comment": f"Strategy: {strategy}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # EXECUTE THE LIVE TRADE
            result = mt5.order_send(request)
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                error_msg = f"Order failed: {result.retcode} - {result.comment}"
                self.logger.error(error_msg)
                return {"status": "error", "reason": error_msg}
            
            # Trade successful!
            trade_info = {
                "status": "executed",
                "order_id": result.order,
                "symbol": symbol,
                "action": action,
                "volume": adjusted_lot_size,
                "price": result.price,
                "strategy": strategy,
                "confidence": confidence,
                "timestamp": time.time()
            }
            
            # Store active order
            self.active_orders[result.order] = trade_info
            
            # Log successful trade
            self.logger.info(f"🚀 LIVE TRADE EXECUTED: {action} {adjusted_lot_size} {symbol} @ {result.price} (Strategy: {strategy})")
            
            # Store trade in Redis for monitoring
            await self.redis_conn.hset_field(f"live_trades:{result.order}", "trade_data", str(trade_info))
            
            return trade_info
            
        except Exception as e:
            error_msg = f"Execution error: {e}"
            self.logger.error(error_msg)
            return {"status": "error", "reason": error_msg}
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get live account information."""
        if not self.is_connected:
            await self.connect()
            
        try:
            account = mt5.account_info()
            if account:
                return {
                    "balance": account.balance,
                    "equity": account.equity,
                    "margin": account.margin,
                    "free_margin": account.margin_free,
                    "margin_level": account.margin_level,
                    "currency": account.currency
                }
        except Exception as e:
            self.logger.error(f"Error getting account info: {e}")
        
        return {}
    
    async def get_open_positions(self) -> Dict[str, Any]:
        """Get currently open positions."""
        if not self.is_connected:
            await self.connect()
            
        try:
            positions = mt5.positions_get()
            if positions:
                position_list = []
                for pos in positions:
                    position_list.append({
                        "ticket": pos.ticket,
                        "symbol": pos.symbol,
                        "type": "BUY" if pos.type == 0 else "SELL",
                        "volume": pos.volume,
                        "price_open": pos.price_open,
                        "price_current": pos.price_current,
                        "profit": pos.profit,
                        "comment": pos.comment
                    })
                return {"positions": position_list, "count": len(position_list)}
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
        
        return {"positions": [], "count": 0}
    
    async def close(self):
        """Close MT5 connection."""
        if self.is_connected:
            mt5.shutdown()
            self.is_connected = False
            self.logger.info("MT5 connection closed")
