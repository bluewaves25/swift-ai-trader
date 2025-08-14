import asyncio
import time
from typing import Dict, Any
from ..memory.recent_context import SystemCoordinationContext
from ..learning_layer.training_module import SystemCoordinationTrainingModule
from ..logs.core_agent_logger import CoreAgentLogger

class SystemCoordinationRetrainingLoop:
    """System coordination retraining loop - focused ONLY on system coordination retraining."""
    
    def __init__(self, training_module: SystemCoordinationTrainingModule, 
                 context: SystemCoordinationContext, interval: int = 3600):
        self.training_module = training_module
        self.context = context
        self.interval = interval
        self.logger = CoreAgentLogger("system_coordination_retraining")
        self.is_running = False

    async def run_coordination_retraining(self):
        """Periodically retrain the system coordination model with new data."""
        self.is_running = True
        
        while self.is_running:
            try:
                self.logger.log_action("start_coordination_retraining", {
                    "interval": self.interval,
                    "timestamp": time.time()
                })
                
                # Prepare coordination dataset
                dataset = self.training_module.prepare_coordination_dataset()
                
                if dataset:
                    # Validate coordination patterns
                    validation_result = self.training_module.validate_coordination_patterns(dataset)
                    
                    if validation_result.get("valid", False):
                        # Train coordination model
                        metrics = self.training_module.train_coordination_model(dataset)
                        
                        self.logger.log_action("coordination_retraining_completed", {
                            "metrics": metrics, 
                            "dataset_size": len(dataset),
                            "validation_score": validation_result.get("validation_score", 0.0)
                        })
                    else:
                        self.logger.log_action("coordination_retraining_skipped", {
                            "result": "skipped", 
                            "reason": "Validation failed",
                            "validation_errors": validation_result.get("validation_errors", [])
                        })
                else:
                    self.logger.log_action("coordination_retraining_skipped", {
                        "result": "skipped", 
                        "reason": "Empty coordination dataset"
                    })
                
                # Wait for next retraining cycle
                await asyncio.sleep(self.interval)
                
            except asyncio.CancelledError:
                self.logger.log_action("coordination_retraining_cancelled", {})
                break
            except Exception as e:
                self.logger.log_action("coordination_retraining_failed", {
                    "result": "failed", 
                    "error": str(e)
                })
                await asyncio.sleep(self.interval)
    
    def stop_coordination_retraining(self):
        """Stop the coordination retraining loop."""
        self.is_running = False
        self.logger.log_action("stop_coordination_retraining", {})
    
    def get_retraining_status(self) -> Dict[str, Any]:
        """Get coordination retraining status."""
        try:
            return {
                "is_running": self.is_running,
                "interval": self.interval,
                "training_module_status": "active",
                "context_status": "active",
                "timestamp": time.time()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def update_retraining_interval(self, new_interval: int):
        """Update the retraining interval."""
        try:
            old_interval = self.interval
            self.interval = new_interval
            
            self.logger.log_action("update_retraining_interval", {
                "old_interval": old_interval,
                "new_interval": new_interval
            })
            
        except Exception as e:
            self.logger.log_action("update_retraining_interval_error", {"error": str(e)})
    
    async def trigger_immediate_retraining(self) -> Dict[str, Any]:
        """Trigger immediate coordination retraining."""
        try:
            self.logger.log_action("trigger_immediate_retraining", {})
            
            # Prepare coordination dataset
            dataset = self.training_module.prepare_coordination_dataset()
            
            if not dataset:
                return {
                    "success": False, 
                    "reason": "Empty coordination dataset"
                }
            
            # Validate coordination patterns
            validation_result = self.training_module.validate_coordination_patterns(dataset)
            
            if not validation_result.get("valid", False):
                return {
                    "success": False, 
                    "reason": "Validation failed",
                    "validation_errors": validation_result.get("validation_errors", [])
                }
            
            # Train coordination model
            metrics = self.training_module.train_coordination_model(dataset)
            
            self.logger.log_action("immediate_retraining_completed", {
                "metrics": metrics,
                "dataset_size": len(dataset)
            })
            
            return {
                "success": True,
                "metrics": metrics,
                "dataset_size": len(dataset)
            }
            
        except Exception as e:
            self.logger.log_action("immediate_retraining_failed", {"error": str(e)})
            return {
                "success": False,
                "error": str(e)
            }