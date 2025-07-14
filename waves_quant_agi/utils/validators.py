### utils/validators.py

import re
from typing import Optional

def is_valid_email(email: str) -> bool:
    """Check if the email address is valid."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def is_strong_password(password: str) -> bool:
    """Check password strength based on length and character mix."""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

def is_valid_uuid(value: str) -> bool:
    """Validate UUID string format."""
    pattern = r"^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$"
    return re.match(pattern, value) is not None

def is_valid_symbol(symbol: str) -> bool:
    """Validate trading symbol format (e.g., BTCUSD, EURUSD)."""
    return symbol.isalnum() and len(symbol) >= 3
