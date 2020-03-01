"""Base classes for generalisations of boards that J5 supports."""

from .arduino import AnaloguePin, ArduinoUno, PinNumber

__all__ = [
    'ArduinoUno',
    'AnaloguePin',
    'PinNumber',
]
