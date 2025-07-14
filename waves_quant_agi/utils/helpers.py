### utils/helpers.py

import uuid
import hashlib
import random
import string
from datetime import datetime
from typing import Any

def generate_uuid() -> str:
    """Generate a unique UUID string."""
    return str(uuid.uuid4())

def hash_string(value: str) -> str:
    """Return the SHA256 hash of a string."""
    return hashlib.sha256(value.encode()).hexdigest()

def generate_random_string(length: int = 12) -> str:
    """Generate a random alphanumeric string of given length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def timestamp_now() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.utcnow().isoformat()

def safe_get(d: dict, key: Any, default: Any = None) -> Any:
    """Safe dictionary access with default value."""
    return d.get(key, default)
