"""
Derived components.

A derived component is a component that can take another component as a parameter.

For example, a device may be attached to various pins on the board, and this could
vary depending on what the user wants. We solve this by passing the pins to the
derived component.
"""

from .ultrasound import UltrasoundInterface, UltrasoundSensor

__all__ = [
    "UltrasoundInterface",
    "UltrasoundSensor",
]
