"""This module contains components, which are the smallest logical element of hardware."""

from .base import Component
from .led import LED, LEDInterface

__all__ = ["Component", "LED", "LEDInterface", "Piezo", "PiezoInterface"]
