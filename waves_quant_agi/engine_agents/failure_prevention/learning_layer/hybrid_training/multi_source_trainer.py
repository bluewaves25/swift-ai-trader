from typing import Dict, Any, List
from ...memory.incident_cache import IncidentCache
from ...logs.failure_agent_logger import FailureAgentLogger
from ..internal.training_module import TrainingModule

class MultiSourceTrainer:
    def __init__(self, internal_trainer: TrainingModule, logger: FailureAgentLogger, cache: IncidentCache):
        self.internal_trainer = internal_trainer
        self.logger = logger
        self.cache = cache

    def prepare_combined_dataset(self, internal_pattern: str = "*", external_pattern: str = "*") -> List[Dict[str, Any]]:
        """Prepare dataset combining internal and external data."""
        try:
            internal_data = self.internal_trainer.prepare_dataset(internal_pattern)
            external_data = self.cache.retrieve_incidents(external_pattern)
            combined_dataset = []

            for data in internal_data:
                combined_dataset.append({
                    "source": "internal",
                    "type": data["type"],
                    "symbol": data["symbol"],
                    "timestamp": data["timestamp"],
                    "features": data["features"]
                })

            for data in external_data:
                combined_dataset.append({
                    "source": data.get("source", "unknown"),
                    "type": data.get("type", "unknown"),
                    "symbol": data.get("symbol", "unknown"),
                    "timestamp": float(data["timestamp"]),
                    "features": {
                        "risk_score": float(data.get("risk_score", 0.0)),
                        "description": data.get("description", ""),
                        "severity": 1.0 if "critical" in data.get("description", "").lower() else 0.5
                    }
                })

            self.logger.log(f"Prepared combined dataset with {len(combined_dataset)} entries")
            return combined_dataset
        except Exception as e:
            self.logger.log(f"Error preparing combined dataset: {e}")
            return []

    def train_model(self, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train model on combined internal and external data (placeholder)."""
        try:
            # Placeholder: Implement model training (e.g., scikit-learn for anomaly detection)
            metrics = {
                "dataset_size": len(dataset),
                "internal_count": sum(1 for d in dataset if d["source"] == "internal"),
                "external_count": sum(1 for d in dataset if d["source"] != "internal"),
                "accuracy": 0.0,  # Placeholder
                "updated": True
            }
            self.logger.log(f"Trained multi-source model with metrics: {metrics}")
            return metrics
        except Exception as e:
            self.logger.log(f"Error training multi-source model: {e}")
            return {"updated": False, "error": str(e)}