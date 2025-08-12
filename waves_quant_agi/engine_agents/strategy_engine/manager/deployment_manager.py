#!/usr/bin/env python3
"""
Deployment Manager - Fixed and Enhanced
Manages strategy deployment with risk and fee checks.
"""

from typing import Dict, Any, List, Optional
import time
import asyncio
from engine_agents.shared_utils import get_shared_redis, get_shared_logger

class DeploymentManager:
    """Deployment manager for strategies with risk and fee validation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = get_shared_logger("strategy_engine", "deployment_manager")
        self.redis_conn = get_shared_redis()
        
        # Risk and fee thresholds
        self.risk_threshold = config.get("risk_threshold", 0.05)  # Max drawdown threshold
        self.fee_threshold = config.get("fee_threshold", 0.01)  # Max fee threshold
        self.max_position_size = config.get("max_position_size", 0.1)  # Max 10% of capital
        self.min_confidence = config.get("min_confidence", 0.6)  # Minimum confidence
        
        # Deployment state
        self.deployed_strategies: Dict[str, Dict[str, Any]] = {}
        self.deployment_history: List[Dict[str, Any]] = []
        
        self.stats = {
            "strategies_deployed": 0,
            "strategies_blocked": 0,
            "deployment_errors": 0,
            "start_time": time.time()
        }

    async def deploy_strategy(self, strategy: Dict[str, Any]) -> bool:
        """Deploy a strategy after comprehensive validation checks."""
        try:
            symbol = strategy.get("symbol", "unknown")
            strategy_id = f"{strategy['type']}:{symbol}:{strategy['timestamp']}"
            
            # Validate strategy structure
            if not self._validate_strategy(strategy):
                self.logger.error(f"Strategy {strategy_id} failed validation")
                return False
            
            # Check risk score
            risk_score = await self._get_risk_score(symbol)
            if risk_score > self.risk_threshold:
                self.logger.warning(f"Strategy {strategy_id} blocked: high risk ({risk_score:.4f})")
                self.stats["strategies_blocked"] += 1
                return False
            
            # Check fee score
            fee_score = await self._get_fee_score(symbol)
            if fee_score > self.fee_threshold:
                self.logger.warning(f"Strategy {strategy_id} blocked: high fees ({fee_score:.4f})")
                self.stats["strategies_blocked"] += 1
                return False
            
            # Check confidence
            confidence = strategy.get("confidence", 0.0)
            if confidence < self.min_confidence:
                self.logger.warning(f"Strategy {strategy_id} blocked: low confidence ({confidence:.2f})")
                self.stats["strategies_blocked"] += 1
                return False
            
            # Check position size
            if not await self._validate_position_size(strategy):
                self.logger.warning(f"Strategy {strategy_id} blocked: invalid position size")
                self.stats["strategies_blocked"] += 1
                return False
            
            # Deploy strategy
            if await self._execute_deployment(strategy, strategy_id):
                self.stats["strategies_deployed"] += 1
                self.logger.info(f"Successfully deployed strategy {strategy_id}")
                return True
            else:
                self.stats["deployment_errors"] += 1
                return False
                
        except Exception as e:
            self.logger.error(f"Error deploying strategy: {e}")
            self.stats["deployment_errors"] += 1
            return False

    def _validate_strategy(self, strategy: Dict[str, Any]) -> bool:
        """Validate strategy structure and required fields."""
        try:
            required_fields = ["type", "timestamp", "action"]
            optional_fields = ["symbol", "confidence", "entry_price", "stop_loss", "take_profit"]
            
            # Check required fields
            for field in required_fields:
                if field not in strategy:
                    self.logger.error(f"Missing required field: {field}")
                    return False
            
            # Check timestamp validity
            timestamp = strategy.get("timestamp", 0)
            if timestamp <= 0 or timestamp > time.time() + 3600:  # Not in future
                self.logger.error(f"Invalid timestamp: {timestamp}")
                return False
            
            # Check action validity
            valid_actions = ["buy", "sell", "hold", "long", "short"]
            action = strategy.get("action", "")
            if action not in valid_actions:
                self.logger.error(f"Invalid action: {action}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating strategy: {e}")
            return False

    async def _get_risk_score(self, symbol: str) -> float:
        """Get risk score for a symbol."""
        try:
            risk_key = f"risk_management:{symbol}:risk_score"
            risk_score = self.redis_conn.get(risk_key)
            
            if risk_score:
                return float(risk_score)
            
            # Default risk score based on asset type
            if any(crypto in symbol.upper() for crypto in ["BTC", "ETH", "USDT", "USDC"]):
                return 0.03  # Crypto: 3% default risk
            elif any(forex in symbol.upper() for forex in ["EUR", "USD", "GBP", "JPY"]):
                return 0.02  # Forex: 2% default risk
            elif any(stock in symbol.upper() for stock in ["AAPL", "MSFT", "GOOGL"]):
                return 0.04  # Stocks: 4% default risk
            else:
                return 0.05  # Default: 5% risk
            
        except Exception as e:
            self.logger.error(f"Error getting risk score: {e}")
            return 0.05  # Conservative default

    async def _get_fee_score(self, symbol: str) -> float:
        """Get fee score for a symbol."""
        try:
            fee_key = f"fee_monitor:{symbol}:fee_score"
            fee_score = self.redis_conn.get(fee_key)
            
            if fee_score:
                return float(fee_score)
            
            # Default fee score based on asset type
            if any(crypto in symbol.upper() for crypto in ["BTC", "ETH", "USDT", "USDC"]):
                return 0.002  # Crypto: 0.2% default fee
            elif any(forex in symbol.upper() for forex in ["EUR", "USD", "GBP", "JPY"]):
                return 0.001  # Forex: 0.1% default fee
            elif any(stock in symbol.upper() for stock in ["AAPL", "MSFT", "GOOGL"]):
                return 0.005  # Stocks: 0.5% default fee
            else:
                return 0.003  # Default: 0.3% fee
            
        except Exception as e:
            self.logger.error(f"Error getting fee score: {e}")
            return 0.003  # Conservative default

    async def _validate_position_size(self, strategy: Dict[str, Any]) -> bool:
        """Validate position size and risk management."""
        try:
            # Get current capital
            capital_key = "trading_engine:capital"
            capital_data = self.redis_conn.get(capital_key)
            
            if not capital_data:
                # Assume default capital if not available
                available_capital = 100000.0
            else:
                import json
                capital_info = json.loads(capital_data)
                available_capital = float(capital_info.get("available_capital", 100000.0))
            
            # Calculate position size
            entry_price = float(strategy.get("entry_price", 0.0))
            if entry_price <= 0:
                return False
            
            # Estimate position value (simplified)
            position_value = entry_price * 1.0  # Assume 1 unit for now
            
            # Check if position size is within limits
            position_ratio = position_value / available_capital if available_capital > 0 else 0
            
            if position_ratio > self.max_position_size:
                self.logger.warning(f"Position size {position_ratio:.2%} exceeds limit {self.max_position_size:.2%}")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating position size: {e}")
            return False

    async def _execute_deployment(self, strategy: Dict[str, Any], strategy_id: str) -> bool:
        """Execute the actual strategy deployment."""
        try:
            # Store in deployed strategies
            self.deployed_strategies[strategy_id] = strategy
            
            # Add to deployment history
            deployment_record = {
                "strategy_id": strategy_id,
                "deployment_time": time.time(),
                "strategy_data": strategy,
                "status": "deployed"
            }
            self.deployment_history.append(deployment_record)
            
            # Store deployment record in Redis with proper JSON serialization
            try:
                import json
                self.redis_conn.set(
                    f"strategy_engine:deployment:{strategy_id}", 
                    json.dumps(deployment_record), 
                    ex=604800
                )
                
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error storing deployment record: {e}")
                return False
            except ConnectionError as e:
                self.logger.error(f"Redis connection error storing deployment record: {e}")
                return False
            except Exception as e:
                self.logger.error(f"Unexpected error storing deployment record: {e}")
                return False
            
            # Notify execution engine
            try:
                self.redis_conn.publish("execution_agent", json.dumps(strategy))
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error notifying execution agent: {e}")
            except ConnectionError as e:
                self.logger.error(f"Redis connection error notifying execution agent: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error notifying execution agent: {e}")
            
            # Log deployment
            self.logger.info(f"Strategy {strategy_id} deployed successfully")
            
            # Notify core
            await self.notify_core({
                "type": "strategy_deployed",
                "strategy_id": strategy_id,
                "timestamp": int(time.time()),
                "description": f"Deployed strategy {strategy_id}"
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error executing deployment: {e}")
            return False

    async def undeploy_strategy(self, strategy_id: str) -> bool:
        """Undeploy a strategy."""
        try:
            if strategy_id not in self.deployed_strategies:
                self.logger.warning(f"Strategy {strategy_id} not found for undeployment")
                return False
            
            # Remove from deployed strategies
            del self.deployed_strategies[strategy_id]
            
            # Update deployment history
            for record in self.deployment_history:
                if record.get("strategy_id") == strategy_id:
                    record["status"] = "undeployed"
                    record["undeployment_time"] = time.time()
                    break
            
            # Remove from Redis
            self.redis_conn.delete(f"strategy_engine:deployed:{strategy_id}")
            
            self.logger.info(f"Strategy {strategy_id} undeployed successfully")
            
            # Notify core
            await self.notify_core({
                "type": "strategy_undeployed",
                "strategy_id": strategy_id,
                "timestamp": int(time.time()),
                "description": f"Undeployed strategy {strategy_id}"
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error undeploying strategy: {e}")
            return False

    async def get_deployed_strategies(self) -> List[Dict[str, Any]]:
        """Get all currently deployed strategies."""
        try:
            return list(self.deployed_strategies.values())
        except Exception as e:
            self.logger.error(f"Error getting deployed strategies: {e}")
            return []

    async def get_deployment_history(self) -> List[Dict[str, Any]]:
        """Get deployment history."""
        try:
            return self.deployment_history.copy()
        except Exception as e:
            self.logger.error(f"Error getting deployment history: {e}")
            return []

    def get_deployment_stats(self) -> Dict[str, Any]:
        """Get deployment manager statistics."""
        return {
            **self.stats,
            "deployed_strategies": len(self.deployed_strategies),
            "uptime": time.time() - self.stats["start_time"]
        }

    async def notify_core(self, issue: Dict[str, Any]):
        """Notify Core Agent of deployment updates."""
        try:
            if not isinstance(issue, dict):
                self.logger.error(f"Invalid issue type: {type(issue)}, expected dict")
                return
                
            self.logger.info(f"Notifying Core Agent: {issue.get('description', 'unknown')}")
            
            # Publish with proper JSON serialization
            try:
                import json
                self.redis_conn.publish("strategy_engine_output", json.dumps(issue))
            except json.JSONEncodeError as e:
                self.logger.error(f"JSON encoding error notifying core: {e}")
                self.stats["errors"] += 1
            except ConnectionError as e:
                self.logger.error(f"Redis connection error notifying core: {e}")
                self.stats["errors"] += 1
            except Exception as e:
                self.logger.error(f"Unexpected error notifying core: {e}")
                self.stats["errors"] += 1
                
        except Exception as e:
            self.logger.error(f"Unexpected error in notify_core: {e}")
            self.stats["errors"] += 1