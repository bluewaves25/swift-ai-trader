#!/usr/bin/env python3
"""
Deployment Manager - Strategy Deployment Management Component
Manages the deployment and activation of trading strategies, integrating with consolidated trading functionality.
Focuses purely on strategy-specific deployment, delegating risk management to the risk management agent.
"""

import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import deque

# Import consolidated trading functionality
from ..interfaces.agent_io import TradingAgentIO
from ..pipeline.execution_pipeline import TradingExecutionPipeline
from ..memory.trading_context import TradingContext

@dataclass
class DeploymentRequest:
    """A strategy deployment request."""
    request_id: str
    strategy_id: str
    deployment_type: str  # live, paper, backtest
    target_environment: str
    parameters: Dict[str, Any]
    priority: int = 5
    created_at: float = None
    status: str = "pending"
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

@dataclass
class DeploymentResult:
    """Result of strategy deployment."""
    result_id: str
    request_id: str
    strategy_id: str
    deployment_type: str
    target_environment: str
    deployment_status: str
    deployment_duration: float
    timestamp: float
    success: bool
    deployment_notes: str = ""

class DeploymentManager:
    """Manages the deployment and activation of trading strategies.
    
    Focuses purely on strategy-specific deployment:
    - Strategy deployment coordination
    - Environment management
    - Deployment validation
    - Deployment monitoring
    
    Risk management is delegated to the risk management agent.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Initialize consolidated trading components
        self.trading_agent_io = TradingAgentIO(config)
        self.trading_execution_pipeline = TradingExecutionPipeline(config)
        self.trading_context = TradingContext(config)
        
        # Deployment management state
        self.deployment_queue: deque = deque(maxlen=100)
        self.active_deployments: Dict[str, DeploymentRequest] = {}
        self.deployment_results: Dict[str, List[DeploymentResult]] = {}
        self.deployment_history: deque = deque(maxlen=1000)
        
        # Deployment settings (strategy-specific only)
        self.deployment_settings = {
            "max_concurrent_deployments": 10,
            "deployment_timeout": 600,  # 10 minutes
            "deployment_environments": ["live", "paper", "backtest"],
            "deployment_validation": True,
            "strategy_parameters": {
                "deployment_retries": 3,
                "validation_timeout": 120,
                "health_check_interval": 30
            }
        }
        
        # Deployment statistics
        self.deployment_stats = {
            "total_deployments": 0,
            "successful_deployments": 0,
            "failed_deployments": 0,
            "pending_deployments": 0,
            "total_deployment_time": 0.0,
            "average_deployment_time": 0.0
        }
        
    async def initialize(self):
        """Initialize the deployment manager."""
        try:
            # Initialize trading components
            await self.trading_agent_io.initialize()
            await self.trading_execution_pipeline.initialize()
            await self.trading_context.initialize()
            
            # Load deployment settings
            await self._load_deployment_settings()
            
            print("✅ Deployment Manager initialized")
            
        except Exception as e:
            print(f"❌ Error initializing Deployment Manager: {e}")
            raise
    
    async def _load_deployment_settings(self):
        """Load deployment management settings from configuration."""
        try:
            deploy_config = self.config.get("strategy_engine", {}).get("deployment_management", {})
            self.deployment_settings.update(deploy_config)
        except Exception as e:
            print(f"❌ Error loading deployment settings: {e}")

    async def add_deployment_request(self, strategy_id: str, deployment_type: str, 
                                   target_environment: str, parameters: Dict[str, Any] = None) -> str:
        """Add a deployment request to the queue."""
        try:
            request_id = f"deploy_{strategy_id}_{int(time.time())}"
            
            request = DeploymentRequest(
                request_id=request_id,
                strategy_id=strategy_id,
                deployment_type=deployment_type,
                target_environment=target_environment,
                parameters=parameters or {}
            )
            
            # Add to deployment queue
            self.deployment_queue.append(request)
            
            # Store request in trading context
            await self.trading_context.store_signal({
                "type": "deployment_request",
                "request_id": request_id,
                "strategy_id": strategy_id,
                "deployment_data": {
                    "type": deployment_type,
                    "target_environment": target_environment,
                    "parameters": parameters
                },
                "timestamp": int(time.time())
            })
            
            # Update statistics
            self.deployment_stats["total_deployments"] += 1
            self.deployment_stats["pending_deployments"] += 1
            
            print(f"✅ Added deployment request: {request_id}")
            return request_id
            
        except Exception as e:
            print(f"❌ Error adding deployment request: {e}")
            return ""

    async def process_deployment_queue(self) -> List[DeploymentResult]:
        """Process the deployment queue."""
        try:
            results = []
            
            while self.deployment_queue and len(self.active_deployments) < self.deployment_settings["max_concurrent_deployments"]:
                request = self.deployment_queue.popleft()
                result = await self._execute_deployment(request)
                if result:
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ Error processing deployment queue: {e}")
            return []

    async def _execute_deployment(self, request: DeploymentRequest) -> Optional[DeploymentResult]:
        """Execute a single deployment request."""
        start_time = time.time()
        
        try:
            # Mark as active
            self.active_deployments[request.request_id] = request
            request.status = "running"
            
            # Validate deployment request
            if not await self._validate_deployment_request(request):
                raise ValueError("Deployment validation failed")
            
            # Execute deployment based on type
            if request.deployment_type == "live":
                deployment_status = await self._deploy_live_strategy(request)
            elif request.deployment_type == "paper":
                deployment_status = await self._deploy_paper_strategy(request)
            elif request.deployment_type == "backtest":
                deployment_status = await self._deploy_backtest_strategy(request)
            else:
                raise ValueError(f"Unknown deployment type: {request.deployment_type}")
            
            # Create deployment result
            result = DeploymentResult(
                result_id=f"result_{request.request_id}",
                request_id=request.request_id,
                strategy_id=request.strategy_id,
                deployment_type=request.deployment_type,
                target_environment=request.target_environment,
                deployment_status=deployment_status,
                deployment_duration=time.time() - start_time,
                timestamp=time.time(),
                success=deployment_status == "deployed",
                deployment_notes=f"Strategy deployed to {request.target_environment}"
            )
            
            # Store result
            if request.strategy_id not in self.deployment_results:
                self.deployment_results[request.strategy_id] = []
            self.deployment_results[request.strategy_id].append(result)
            
            # Update statistics
            if result.success:
                self.deployment_stats["successful_deployments"] += 1
            else:
                self.deployment_stats["failed_deployments"] += 1
            
            self.deployment_stats["pending_deployments"] -= 1
            self.deployment_stats["total_deployment_time"] += result.deployment_duration
            
            # Store result in trading context
            await self.trading_context.store_signal({
                "type": "deployment_result",
                "strategy_id": request.strategy_id,
                "result_data": {
                    "deployment_type": request.deployment_type,
                    "target_environment": request.target_environment,
                    "status": deployment_status,
                    "success": result.success
                },
                "timestamp": int(time.time())
            })
            
            print(f"✅ Deployment completed: {request.request_id}")
            return result
            
        except Exception as e:
            print(f"❌ Error executing deployment: {e}")
            self.deployment_stats["failed_deployments"] += 1
            self.deployment_stats["pending_deployments"] -= 1
            
            # Return failed result
            return DeploymentResult(
                result_id=f"failed_{request.request_id}",
                request_id=request.request_id,
                strategy_id=request.strategy_id,
                deployment_type=request.deployment_type,
                target_environment=request.target_environment,
                deployment_status="failed",
                deployment_duration=time.time() - start_time,
                timestamp=time.time(),
                success=False,
                deployment_notes=f"Deployment failed: {str(e)}"
            )
        finally:
            # Remove from active deployments
            self.active_deployments.pop(request.request_id, None)

    async def _validate_deployment_request(self, request: DeploymentRequest) -> bool:
        """Validate deployment request (strategy-specific validation only).
        
        This does NOT include risk management validation.
        """
        try:
            # Basic parameter validation
            if not request.strategy_id or not request.deployment_type or not request.target_environment:
                return False
            
            # Deployment type validation
            if request.deployment_type not in self.deployment_settings["deployment_environments"]:
                return False
            
            # Target environment validation
            if request.target_environment not in self.deployment_settings["deployment_environments"]:
                return False
            
            # Parameter validation
            if not self._validate_deployment_parameters(request.parameters):
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error validating deployment request: {e}")
            return False

    def _validate_deployment_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Validate deployment parameters."""
        try:
            # Check for required parameters
            required_params = ["strategy_config", "environment_config"]
            for param in required_params:
                if param not in parameters:
                    print(f"❌ Missing required parameter: {param}")
                    return False
            
            # Validate strategy configuration
            strategy_config = parameters.get("strategy_config", {})
            if not isinstance(strategy_config, dict):
                return False
            
            # Validate environment configuration
            environment_config = parameters.get("environment_config", {})
            if not isinstance(environment_config, dict):
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error validating deployment parameters: {e}")
            return False

    async def _deploy_live_strategy(self, request: DeploymentRequest) -> str:
        """Deploy strategy to live environment."""
        try:
            # Send deployment request to execution pipeline
            deployment_result = await self.trading_execution_pipeline.send_to_execution({
                "type": "strategy_deployment",
                "strategy_id": request.strategy_id,
                "deployment_type": "live",
                "target_environment": request.target_environment,
                "parameters": request.parameters
            })
            
            if deployment_result.get("success", False):
                # Notify other agents about live deployment
                await self.trading_agent_io.broadcast_to_all_trading_agents({
                    "type": "strategy_live_deployment",
                    "strategy_id": request.strategy_id,
                    "deployment_info": deployment_result
                })
                
                return "deployed"
            else:
                return "failed"
                
        except Exception as e:
            print(f"❌ Error deploying live strategy: {e}")
            return "failed"

    async def _deploy_paper_strategy(self, request: DeploymentRequest) -> str:
        """Deploy strategy to paper trading environment."""
        try:
            # Send deployment request to execution pipeline
            deployment_result = await self.trading_execution_pipeline.send_to_execution({
                "type": "strategy_deployment",
                "strategy_id": request.strategy_id,
                "deployment_type": "paper",
                "target_environment": request.target_environment,
                "parameters": request.parameters
            })
            
            if deployment_result.get("success", False):
                # Notify other agents about paper deployment
                await self.trading_agent_io.broadcast_to_all_trading_agents({
                    "type": "strategy_paper_deployment",
                    "strategy_id": request.strategy_id,
                    "deployment_info": deployment_result
                })
                
                return "deployed"
            else:
                return "failed"
                
        except Exception as e:
            print(f"❌ Error deploying paper strategy: {e}")
            return "failed"

    async def _deploy_backtest_strategy(self, request: DeploymentRequest) -> str:
        """Deploy strategy to backtest environment."""
        try:
            # Send deployment request to execution pipeline
            deployment_result = await self.trading_execution_pipeline.send_to_execution({
                "type": "strategy_deployment",
                "strategy_id": request.strategy_id,
                "deployment_type": "backtest",
                "target_environment": request.target_environment,
                "parameters": request.parameters
            })
            
            if deployment_result.get("success", False):
                # Notify other agents about backtest deployment
                await self.trading_agent_io.broadcast_to_all_trading_agents({
                    "type": "strategy_backtest_deployment",
                    "strategy_id": request.strategy_id,
                    "deployment_info": deployment_result
                })
                
                return "deployed"
            else:
                return "failed"
                
        except Exception as e:
            print(f"❌ Error deploying backtest strategy: {e}")
            return "failed"

    async def cancel_deployment(self, request_id: str) -> bool:
        """Cancel a pending deployment."""
        try:
            # Find deployment in queue
            for i, request in enumerate(self.deployment_queue):
                if request.request_id == request_id:
                    # Remove from queue
                    self.deployment_queue.pop(i)
                    
                    # Update statistics
                    self.deployment_stats["pending_deployments"] -= 1
                    
                    # Store cancellation in trading context
                    await self.trading_context.store_signal({
                        "type": "deployment_cancellation",
                        "request_id": request_id,
                        "strategy_id": request.strategy_id,
                        "cancellation_data": {
                            "reason": "user_requested",
                            "timestamp": int(time.time())
                        },
                        "timestamp": int(time.time())
                    })
                    
                    print(f"✅ Deployment cancelled: {request_id}")
                    return True
            
            # Check if deployment is active
            if request_id in self.active_deployments:
                request = self.active_deployments[request_id]
                request.status = "cancelled"
                
                # Update statistics
                self.deployment_stats["pending_deployments"] -= 1
                
                print(f"✅ Active deployment cancelled: {request_id}")
                return True
            
            print(f"⚠️ Deployment not found: {request_id}")
            return False
            
        except Exception as e:
            print(f"❌ Error cancelling deployment: {e}")
            return False

    async def get_deployment_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific deployment."""
        try:
            # Check active deployments
            if request_id in self.active_deployments:
                request = self.active_deployments[request_id]
                return {
                    "request_id": request_id,
                    "status": request.status,
                    "strategy_id": request.strategy_id,
                    "deployment_type": request.deployment_type,
                    "target_environment": request.target_environment,
                    "created_at": request.created_at
                }
            
            # Check queue
            for request in self.deployment_queue:
                if request.request_id == request_id:
                    return {
                        "request_id": request_id,
                        "status": "queued",
                        "strategy_id": request.strategy_id,
                        "deployment_type": request.deployment_type,
                        "target_environment": request.target_environment,
                        "created_at": request.created_at
                    }
            
            # Check results
            for strategy_id, results in self.deployment_results.items():
                for result in results:
                    if result.request_id == request_id:
                        return {
                            "request_id": request_id,
                            "status": "completed" if result.success else "failed",
                            "strategy_id": result.strategy_id,
                            "deployment_type": result.deployment_type,
                            "target_environment": result.target_environment,
                            "deployment_status": result.deployment_status,
                            "success": result.success,
                            "notes": result.deployment_notes
                        }
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting deployment status: {e}")
            return None

    async def get_deployments_by_strategy(self, strategy_id: str) -> List[Dict[str, Any]]:
        """Get all deployments for a specific strategy."""
        try:
            deployments = []
            
            # Get deployments from queue
            for request in self.deployment_queue:
                if request.strategy_id == strategy_id:
                    deployments.append({
                        "request_id": request.request_id,
                        "status": "queued",
                        "deployment_type": request.deployment_type,
                        "target_environment": request.target_environment,
                        "created_at": request.created_at
                    })
            
            # Get active deployments
            for request_id, request in self.active_deployments.items():
                if request.strategy_id == strategy_id:
                    deployments.append({
                        "request_id": request_id,
                        "status": request.status,
                        "deployment_type": request.deployment_type,
                        "target_environment": request.target_environment,
                        "created_at": request.created_at
                    })
            
            # Get completed deployments
            if strategy_id in self.deployment_results:
                for result in self.deployment_results[strategy_id]:
                    deployments.append({
                        "request_id": result.request_id,
                        "status": "completed" if result.success else "failed",
                        "deployment_type": result.deployment_type,
                        "target_environment": result.target_environment,
                        "deployment_status": result.deployment_status,
                        "success": result.success,
                        "notes": result.deployment_notes
                    })
            
            return deployments
            
        except Exception as e:
            print(f"❌ Error getting deployments by strategy: {e}")
            return []

    async def get_deployment_summary(self) -> Dict[str, Any]:
        """Get summary of deployment management statistics."""
        try:
            # Calculate average deployment time
            if self.deployment_stats["successful_deployments"] > 0:
                avg_deployment_time = self.deployment_stats["total_deployment_time"] / self.deployment_stats["successful_deployments"]
            else:
                avg_deployment_time = 0.0
            
            return {
                "stats": {**self.deployment_stats, "average_deployment_time": avg_deployment_time},
                "queue_size": len(self.deployment_queue),
                "active_deployments": len(self.active_deployments),
                "deployment_history_size": len(self.deployment_history),
                "deployment_settings": self.deployment_settings
            }
            
        except Exception as e:
            print(f"❌ Error getting deployment summary: {e}")
            return {}

    async def cleanup(self):
        """Clean up resources."""
        try:
            await self.trading_agent_io.cleanup()
            await self.trading_execution_pipeline.cleanup()
            await self.trading_context.cleanup()
            print("✅ Deployment Manager cleaned up")
        except Exception as e:
            print(f"❌ Error cleaning up Deployment Manager: {e}")