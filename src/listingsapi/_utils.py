"""Internal utilities."""

from __future__ import annotations

import base64


def encode_location_id(id_value: str | int) -> str:
    """Convert a numeric location ID to base64-encoded form, or return as-is if already encoded."""
    if isinstance(id_value, int):
        return base64.b64encode(f"Location:{id_value}".encode()).decode("ascii")
    s = str(id_value).strip()
    if s.isdigit():
        return base64.b64encode(f"Location:{s}".encode()).decode("ascii")
    return s
