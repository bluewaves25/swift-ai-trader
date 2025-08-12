#!/usr/bin/env python3
"""
Enhanced Execution Agent V2
Rust-based execution agent with Python learning layer integration.
Inherits from BaseAgent to eliminate infrastructure duplication.
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
import pandas as pd

from engine_agents.shared_utils.base_agent import BaseAgent
from .python_bridge import ExecutionBridge

class EnhancedExecutionAgentV2(BaseAgent):
    """
    Enhanced execution agent that inherits from BaseAgent.
    Focuses ONLY on business logic, not infrastructure.
    """
    
    def _initialize_agent_components(self):
        """Initialize execution-specific components."""
        self.execution_bridge = ExecutionBridge(self.config)
        self.signal_queue = []
        self.execution_stats = {
            "total_signals_processed": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "pending_signals": 0,
            "last_execution_time": None
        }
        
        # Execution configuration
        self.execution_config = {
            "max_slippage": self.config.get("max_slippage", 0.001),
            "execution_timeout": self.config.get("execution_timeout", 30),
            "retry_attempts": self.config.get("retry_attempts", 3),
            "batch_size": self.config.get("batch_size", 10)
        }
    
    async def _agent_specific_startup(self):
        """Initialize execution-specific components."""
        try:
            # Initialize execution bridge (but don't start it yet)
            self.execution_bridge = ExecutionBridge(self.config)
            
            # Don't start background tasks here - let BaseAgent handle them
            self.logger.info("✅ Execution agent initialization completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in execution startup: {e}")
            raise
    
    async def _agent_specific_shutdown(self):
        """Shutdown execution-specific components."""
        try:
            if hasattr(self, 'execution_bridge'):
                await self.execution_bridge.stop()
            
            self.logger.info("✅ Execution agent shutdown completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error in execution shutdown: {e}")
    
    async def _initialize_signal_processing(self):
        """Initialize signal processing capabilities."""
        try:
            # Set up signal monitoring
            self.logger.info("Initializing signal processing...")
            
            # Start signal monitoring task
            signal_task = asyncio.create_task(
                self._signal_monitoring_loop(), 
                name="execution_signal_monitor"
            )
            self._background_tasks.append(signal_task)
            
        except Exception as e:
            self.logger.error(f"Error initializing signal processing: {e}")
            raise
    
    async def _signal_monitoring_loop(self):
        """Monitor for new trading signals."""
        # Wait for trading engine to be ready
        self.logger.info("⏳ Waiting for trading engine to be ready...")
        await self._wait_for_trading_engine()
        self.logger.info("✅ Trading engine is ready, starting signal processing...")
        
        while self.is_running:
            try:
                # Check for new signals
                await self._process_pending_signals()
                
                # Update execution statistics
                await self._update_execution_stats()
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.error(f"Error in signal monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _wait_for_trading_engine(self):
        """Wait for trading engine to be ready before starting execution."""
        max_wait_time = 300  # 5 minutes max wait
        start_time = time.time()
        
        while self.is_running and (time.time() - start_time) < max_wait_time:
            try:
                                    # Check if trading engine is running
                    if self.redis_conn:
                        # Check trading engine status
                        trading_engine_stats = self.redis_conn.hgetall('agent_stats:trading_engine')
                        if trading_engine_stats:
                            status = trading_engine_stats.get('status', 'unknown')
                            if status == 'running':
                                self.logger.info("✅ Trading engine detected as running")
                                return
                        
                        # Check for trading engine ready signal
                        ready_signal = self.redis_conn.get('trading_engine_ready')
                        if ready_signal:
                            self.logger.info("✅ Trading engine ready signal received")
                            return
                        
                        # Also check if there are any execution orders (indicates trading engine is working)
                        execution_orders_count = self.redis_conn.llen('execution_orders')
                        if execution_orders_count > 0:
                            self.logger.info(f"✅ Trading engine is working (found {execution_orders_count} orders)")
                            return
                
                self.logger.info("⏳ Waiting for trading engine... (checking every 10 seconds)")
                await asyncio.sleep(10)
                
            except Exception as e:
                self.logger.warning(f"Error checking trading engine status: {e}")
                await asyncio.sleep(10)
        
        if (time.time() - start_time) >= max_wait_time:
            self.logger.warning("⚠️ Timeout waiting for trading engine, proceeding anyway...")
        else:
            self.logger.info("✅ Trading engine ready signal received")
    
    async def _process_pending_signals(self):
        """Process any pending trading signals."""
        try:
            if not self.redis_conn:
                self.logger.warning("No Redis connection available")
                return
            
            # Get signals from execution_orders (where trading engine sends them)
            signals = self.redis_conn.lrange("execution_orders", 0, -1)
            
            if signals:
                self.logger.info(f"Found {len(signals)} signals to process")
                
                # Process signals in batches to avoid overwhelming
                batch_size = min(len(signals), self.execution_config["batch_size"])
                signals_to_process = signals[:batch_size]
                
                self.logger.info(f"Processing batch of {len(signals_to_process)} signals")
                
                for i, signal_data in enumerate(signals_to_process):
                    try:
                        self.logger.info(f"Processing signal {i+1}/{len(signals_to_process)}")
                        
                        signal = json.loads(signal_data)
                        self.logger.info(f"Signal data: {signal}")
                        
                        # Transform signal to execution format
                        execution_signal = self._transform_signal_for_execution(signal)
                        
                        if execution_signal:
                            self.logger.info(f"Executing transformed signal: {execution_signal}")
                            success = await self._execute_signal(execution_signal)
                            
                            if success:
                                # Remove processed signal from execution_orders
                                removed = self.redis_conn.lrem("execution_orders", 1, signal_data)
                                self.logger.info(f"Removed processed signal: {removed} items removed")
                            else:
                                self.logger.error(f"Signal execution failed, keeping in queue")
                        else:
                            self.logger.warning(f"Could not transform signal: {signal}")
                            # Remove untransformable signal to prevent infinite retries
                            removed = self.redis_conn.lrem("execution_orders", 1, signal_data)
                            self.logger.info(f"Removed untransformable signal: {removed} items removed")
                            
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Invalid signal format: {signal_data}, error: {e}")
                        # Remove invalid signal
                        removed = self.redis_conn.lrem("execution_orders", 1, signal_data)
                        self.logger.info(f"Removed invalid signal: {removed} items removed")
                    except Exception as e:
                        self.logger.error(f"Error processing signal: {e}")
                        # Remove failed signal to prevent infinite retries
                        removed = self.redis_conn.lrem("execution_orders", 1, signal_data)
                        self.logger.info(f"Removed failed signal: {removed} items removed")
            else:
                # No signals to process
                self.logger.debug("No signals to process")
                    
        except Exception as e:
            self.logger.error(f"Error in signal processing: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
    
    def _transform_signal_for_execution(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Transform trading engine order to execution format."""
        try:
            # Extract required fields from trading engine order
            symbol = signal.get('symbol', '')
            action = signal.get('action', '').lower()
            price = signal.get('price', 0)
            quantity = signal.get('quantity', 0.01)
            
            if not symbol or not action or not price:
                self.logger.warning(f"Missing required fields in signal: {signal}")
                return None
            
            # Transform action to execution format
            if action == 'buy':
                exec_action = 'buy'
            elif action == 'sell':
                exec_action = 'sell'
            else:
                self.logger.warning(f"Invalid action: {action}")
                return None
            
            # Create execution signal with required fields
            execution_signal = {
                'id': f"exec_{int(time.time() * 1000)}",  # Generate unique ID
                'symbol': symbol,
                'action': exec_action,
                'quantity': quantity,
                'price': price,
                'stop_loss': signal.get('stop_loss', price * 0.995),
                'take_profit': signal.get('take_profit', price * 1.01),
                'strategy': signal.get('strategy', 'unknown'),
                'confidence': signal.get('confidence', 0.5),
                'reason': signal.get('reason', 'strategy_signal'),
                'timestamp': signal.get('timestamp', time.time())
            }
            
            self.logger.info(f"Transformed order: {symbol} {action} {quantity} @ {price}")
            return execution_signal
            
        except Exception as e:
            self.logger.error(f"Error transforming signal: {e}")
            return None
    
    async def _execute_signal(self, signal: Dict[str, Any]):
        """Execute a trading signal via MT5."""
        try:
            self.logger.info(f"Executing signal: {signal.get('id', 'unknown')}")
            
            # Validate signal
            if not self._validate_execution_signal(signal):
                self.logger.warning(f"Invalid signal: {signal}")
                return False
            
            # Execute via MT5
            success = await self._execute_mt5_order(signal)
            
            if success:
                self.execution_stats["successful_executions"] += 1
                self.execution_stats["last_execution_time"] = time.time()
                self.logger.info(f"✅ Signal executed successfully: {signal.get('id')}")
            else:
                self.execution_stats["failed_executions"] += 1
                self.logger.error(f"❌ Signal execution failed: {signal.get('id')}")
            
            self.execution_stats["total_signals_processed"] += 1
            return success
            
        except Exception as e:
            self.logger.error(f"Error executing signal: {e}")
            self.execution_stats["failed_executions"] += 1
            return False
    
    async def _execute_mt5_order(self, signal: Dict[str, Any]) -> bool:
        """Execute order via MetaTrader 5."""
        try:
            # Import MT5 module
            import MetaTrader5 as mt5
            
            # Initialize MT5 if not already done
            if not mt5.initialize():
                self.logger.error("❌ Failed to initialize MT5")
                return False
            
            # Prepare order request
            symbol = signal.get('symbol', '')
            action = signal.get('action', '').lower()
            quantity = signal.get('quantity', 0.01)
            price = signal.get('price', 0)
            stop_loss = signal.get('stop_loss', 0)
            take_profit = signal.get('take_profit', 0)
            
            # Create order request
            if action == 'buy':
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(symbol).ask if mt5.symbol_info_tick(symbol) else price
            elif action == 'sell':
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(symbol).bid if mt5.symbol_info_tick(symbol) else price
            else:
                self.logger.error(f"Invalid action: {action}")
                return False
            
            # Create order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": quantity,
                "type": order_type,
                "price": price,
                "deviation": 20,
                "magic": 234000,
                "comment": f"AI_{signal.get('strategy', 'unknown')}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Add stop loss and take profit if provided
            if stop_loss > 0:
                request["sl"] = stop_loss
            if take_profit > 0:
                request["tp"] = take_profit
            
            # Execute order
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                self.logger.info(f"✅ MT5 order executed: {symbol} {action} {quantity} @ {price}")
                
                # Update MT5 connection status
                if self.redis_conn:
                    mt5_status = {
                        'connected': 'true',
                        'last_check': str(time.time()),
                        'error_count': '0',
                        'last_error': 'none'
                    }
                    self.redis_conn.hset('mt5_connection_status', mapping=mt5_status)
                
                return True
            else:
                self.logger.error(f"❌ MT5 order failed: {result.retcode} - {result.comment}")
                
                # Update MT5 connection status with error
                if self.redis_conn:
                    mt5_status = {
                        'connected': 'false',
                        'last_check': str(time.time()),
                        'error_count': str(int(self.execution_stats.get('failed_executions', 0)) + 1),
                        'last_error': f"{result.retcode}: {result.comment}"
                    }
                    self.redis_conn.hset('mt5_connection_status', mapping=mt5_status)
                
                return False
                
        except ImportError:
            self.logger.error("❌ MetaTrader5 module not installed. Install with: pip install MetaTrader5")
            return False
        except Exception as e:
            self.logger.error(f"❌ MT5 execution error: {e}")
            
            # Update MT5 connection status with error
            if self.redis_conn:
                mt5_status = {
                    'connected': 'false',
                    'last_check': str(time.time()),
                    'error_count': str(int(self.execution_stats.get('failed_executions', 0)) + 1),
                    'last_error': str(e)
                }
                self.redis_conn.hset('mt5_connection_status', mapping=mt5_status)
            
            return False
    
    def _validate_execution_signal(self, signal: Dict[str, Any]) -> bool:
        """Validate execution signal format and content."""
        required_fields = ["symbol", "action", "quantity", "price"]
        
        # Check required fields
        for field in required_fields:
            if field not in signal:
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate action
        if signal["action"] not in ["buy", "sell", "close"]:
            self.logger.warning(f"Invalid action: {signal['action']}")
            return False
        
        # Validate quantity
        if not isinstance(signal["quantity"], (int, float)) or signal["quantity"] <= 0:
            self.logger.warning(f"Invalid quantity: {signal['quantity']}")
            return False
        
        # Validate price
        if not isinstance(signal["price"], (int, float)) or signal["price"] <= 0:
            self.logger.warning(f"Invalid price: {signal['price']}")
            return False
        
        return True
    
    async def _update_execution_stats(self):
        """Update execution statistics."""
        try:
            # Update pending signals count from execution_orders
            if self.redis_conn:
                pending_count = self.redis_conn.llen("execution_orders")
                self.execution_stats["pending_signals"] = pending_count
            
            # Store stats in Redis for monitoring
            if self.redis_conn:
                self.redis_conn.hset(
                    f"agent_stats:{self.agent_name}",
                    mapping=self.execution_stats
                )
                
        except Exception as e:
            self.logger.error(f"Error updating execution stats: {e}")
    
    async def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status."""
        return {
            "agent_name": self.agent_name,
            "is_running": self.is_running,
            "execution_stats": self.execution_stats,
            "execution_config": self.execution_config,
            "bridge_status": await self.execution_bridge.get_bridge_status() if hasattr(self, 'execution_bridge') else None
        }
    
    async def send_execution_signal(self, signal: Dict[str, Any]) -> bool:
        """Send a signal for execution."""
        try:
            if not self.is_running:
                self.logger.warning("Execution agent not running")
                return False
            
            # Add signal to queue
            self.signal_queue.append(signal)
            
            # Store in Redis for processing
            if self.redis_conn:
                self.redis_conn.rpush("execution:signals", json.dumps(signal))
            
            self.logger.info(f"Signal queued for execution: {signal.get('id')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error queuing signal: {e}")
            return False
    
    def _get_background_tasks(self) -> List[tuple]:
        """Get background tasks for this agent."""
        return [
            (self._signal_monitoring_loop(), "Signal Monitoring", "high")
        ]
