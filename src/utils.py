"""Utility functions for the routing system."""

import json
from typing import Any, Dict


def serialize_json(obj: Any) -> str:
    """Serialize complex objects to JSON."""
    if isinstance(obj, dict):
        return json.dumps(obj, default=str)
    return str(obj)


def validate_query(query: str, max_length: int = 10000) -> tuple:
    """Validate incoming query parameters."""
    if not query or not query.strip():
        return False, "Empty query provided"
    
    if len(query) > max_length:
        return False, f"Query exceeds maximum length of {max_length}"
    
    return True, "Valid"


def format_currency(amount: float) -> str:
    """Format amount as USD currency string."""
    return f"${amount:.6f}"


def truncate_string(s: str, max_len: int = 50) -> str:
    """Truncate string for display purposes."""
    if len(s) <= max_len:
        return s
    return s[:max_len-3] + "..."
