"""Base classes for generalisations of boards that J5 supports."""

from .arduino import AnaloguePin, ArduinoUno

__all__ = [
    'ArduinoUno',
    'AnaloguePin'
]
