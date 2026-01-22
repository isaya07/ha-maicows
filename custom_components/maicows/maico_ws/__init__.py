"""Maico WS API package for Modbus communication."""

from __future__ import annotations

from .client import MaicoWSClient
from .controls import ControlsMixin
from .registers import MaicoWSRegisters
from .sensors import SensorsMixin
from .status import StatusMixin


class MaicoWS(MaicoWSClient, SensorsMixin, ControlsMixin, StatusMixin):
    """Maico WS VMC API class combining all functionality."""


# Backward compatibility aliases
MaicoWS320B = MaicoWS
MaicoWS320BRegisters = MaicoWSRegisters

__all__ = [
    "MaicoWS",
    "MaicoWS320B",
    "MaicoWS320BRegisters",
    "MaicoWSClient",
    "MaicoWSRegisters",
]
