import asyncio
from typing import Dict, Any
from ..cache.db_connector import DBConnector
from .training_module import TrainingModule

class RetrainingLoop:
    def __init__(self, training_module: TrainingModule, db: DBConnector, interval: int = 3600):
        self.training_module = training_module
        self.db = db
        self.interval = interval  # seconds

    async def run_retraining(self):
        """Periodically retrain the model with new data."""
        while True:
            try:
                dataset = self.training_module.prepare_dataset()
                if dataset:
                    metrics = self.training_module.train_model(dataset)
                    print(f"Retraining completed: {metrics}")
                else:
                    print("No data for retraining")
                await asyncio.sleep(self.interval)
            except Exception as e:
                print(f"Error in retraining loop: {e}")
                await asyncio.sleep(self.interval)