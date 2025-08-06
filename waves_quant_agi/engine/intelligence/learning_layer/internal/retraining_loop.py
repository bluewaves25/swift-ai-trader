import asyncio
from typing import Dict, Any
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache
from .training_module import TrainingModule

class RetrainingLoop:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache, training_module: TrainingModule):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.training_module = training_module
        self.retrain_interval = config.get("retrain_interval", 86400)  # Daily in seconds

    async def run_retraining(self):
        """Run periodic retraining of the coordination model."""
        try:
            while True:
                self.logger.log("Starting retraining loop")
                dataset = await self.training_module.prepare_dataset()
                metrics = await self.training_module.train_model(dataset)
                if metrics:
                    self.logger.log(f"Retraining completed: {metrics.get('description', 'unknown')}")
                else:
                    self.logger.log("Retraining failed: no metrics returned")
                await asyncio.sleep(self.retrain_interval)
        except Exception as e:
            self.logger.log(f"Error in retraining loop: {e}")
            self.cache.store_incident({
                "type": "retraining_error",
                "timestamp": int(time.time()),
                "description": f"Error in retraining loop: {str(e)}"
            })

    def start(self):
        """Start the retraining loop."""
        asyncio.run(self.run_retraining())