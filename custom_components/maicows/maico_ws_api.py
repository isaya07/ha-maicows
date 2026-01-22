"""
Maico WS API module - backward compatibility layer.

This module re-exports from the maico_ws package for backward compatibility.
New code should import directly from `maico_ws` subpackage.
"""

from __future__ import annotations

# Re-export everything from the new package structure
from .maico_ws import (
    MaicoWS,
    MaicoWS320B,
    MaicoWS320BRegisters,
    MaicoWSClient,
    MaicoWSRegisters,
)

__all__ = [
    "MaicoWS",
    "MaicoWS320B",
    "MaicoWS320BRegisters",
    "MaicoWSClient",
    "MaicoWSRegisters",
]
