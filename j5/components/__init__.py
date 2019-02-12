"""This module contains components, which are the smallest logical element of hardware."""

from .base import Component
from .button import Button, ButtonInterface
from .led import LED, LEDInterface

__all__ = ["Component", "Button", "ButtonInterface", "LED", "LEDInterface", "Piezo", "PiezoInterface"]
