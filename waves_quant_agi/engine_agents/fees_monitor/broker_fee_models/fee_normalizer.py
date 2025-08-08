from typing import Dict, Any
from ..logs.failure_agent_logger import FailureAgentLogger
from ..memory.incident_cache import IncidentCache
from .model_loader import ModelLoader

class FeeNormalizer:
    def __init__(self, config: Dict[str, Any], logger: FailureAgentLogger, cache: IncidentCache, model_loader: ModelLoader):
        self.config = config
        self.logger = logger
        self.cache = cache
        self.model_loader = model_loader
        self.base_currency = config.get("base_currency", "USD")
        self.normalized_fields = ["commission", "swap", "inactivity_fee", "spread"]

    def normalize_fee_model(self, broker: str, fee_model: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize broker fee model to a standard format and currency."""
        try:
            normalized = {
                "broker": broker,
                "timestamp": int(time.time()),
                "fees": {}
            }
            for field in self.normalized_fields:
                value = fee_model.get(field, 0.0)
                if isinstance(value, (int, float)):
                    normalized["fees"][field] = self._convert_to_base_currency(value, fee_model.get("currency", self.base_currency))
                else:
                    normalized["fees"][field] = 0.0
                    self.logger.log(f"Invalid {field} for {broker}: {value}")
            
            self.cache.store_incident({
                "type": "fee_model_normalized",
                "broker": broker,
                "timestamp": normalized["timestamp"],
                "description": f"Normalized fee model for {broker}: {normalized['fees']}"
            })
            self.model_loader.update_fee_model(broker, normalized)
            self.logger.log(f"Normalized fee model for {broker}")
            return normalized
        except Exception as e:
            self.logger.log(f"Error normalizing fee model for {broker}: {e}")
            self.cache.store_incident({
                "type": "fee_normalize_error",
                "broker": broker,
                "timestamp": int(time.time()),
                "description": f"Error normalizing fee model for {broker}: {str(e)}"
            })
            return {}

    def _convert_to_base_currency(self, value: float, currency: str) -> float:
        """Convert fee value to base currency (placeholder)."""
        try:
            # Placeholder: Implement currency conversion (e.g., using an API like exchangeratesapi.io)
            if currency != self.base_currency:
                self.logger.log(f"Currency conversion needed: {currency} to {self.base_currency}")
                return value  # Mock: assumes 1:1 for now
            return value
        except Exception as e:
            self.logger.log(f"Error converting currency {currency}: {e}")
            return value