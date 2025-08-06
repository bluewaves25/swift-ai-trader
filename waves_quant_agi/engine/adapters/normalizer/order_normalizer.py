from typing import Dict, Any
from ..logs.broker_logger import BrokerLogger

class OrderNormalizer:
    def __init__(self):
        self.logger = BrokerLogger("normalizer")
        self.standard_format = {
            "base": str,
            "quote": str,
            "side": str,  # buy/sell
            "type": str,  # market/limit
            "amount": float,
            "price": float,  # optional for market orders
        }

    def normalize(self, order: Dict[str, Any], broker_name: str) -> Dict[str, Any]:
        """Translate internal order to standard format for broker."""
        normalized = {}
        try:
            for key, expected_type in self.standard_format.items():
                if key in order:
                    normalized[key] = expected_type(order[key])
                elif key != "price":  # price is optional
                    raise ValueError(f"Missing required field: {key}")
            normalized["side"] = normalized["side"].lower()
            normalized["type"] = normalized["type"].lower()
            self.logger.log_request("normalize", {"input": order, "output": normalized})
            return normalized
        except Exception as e:
            self.logger.log_request("normalize", {"input": order, "error": str(e)})
            raise

    def validate(self, order: Dict[str, Any]) -> bool:
        """Validate if order matches standard format."""
        try:
            for key, expected_type in self.standard_format.items():
                if key != "price" and key not in order:
                    return False
                if key in order and not isinstance(order[key], expected_type):
                    return False
            return True
        except Exception:
            return False