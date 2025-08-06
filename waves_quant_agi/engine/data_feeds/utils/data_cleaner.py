from typing import Dict, Any, Optional
import re

class DataCleaner:
    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize data."""
        try:
            cleaned_data = {}
            for key, value in data.items():
                if isinstance(value, str):
                    # Remove special characters, trim whitespace
                    cleaned_data[key] = re.sub(r'[^\w\s./-]', '', value.strip())
                elif isinstance(value, float):
                    # Round to 8 decimals for consistency
                    cleaned_data[key] = round(value, 8)
                elif isinstance(value, list) and key in {"bids", "asks"}:
                    # Clean order book entries
                    cleaned_data[key] = [[round(float(price), 8), round(float(amount), 8)] for price, amount in value]
                else:
                    cleaned_data[key] = value
            return cleaned_data
        except Exception as e:
            print(f"Error cleaning data: {e}")
            return data