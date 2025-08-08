from typing import Dict, Any, Optional

class SchemaValidator:
    def validate(self, data: Dict[str, Any], schema: Dict[str, type]) -> bool:
        """Validate data against a schema."""
        try:
            for key, expected_type in schema.items():
                if key not in data:
                    print(f"Missing key: {key}")
                    return False
                if not isinstance(data[key], expected_type):
                    print(f"Invalid type for {key}: expected {expected_type}, got {type(data[key])}")
                    return False
            return True
        except Exception as e:
            print(f"Error validating schema: {e}")
            return False