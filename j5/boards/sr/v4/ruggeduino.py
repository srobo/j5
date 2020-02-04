"""
Classes for the Student Robotics Ruggeduino.

It's similar to the Sourcebots Arduino, but without official ultrasound support.
"""
from enum import IntEnum
from typing import Optional, Set, Type, Union

from j5.backends import Backend
from j5.boards.j5 import ArduinoUno
from j5.components import (
    LED,
    Component,
    GPIOPin,
)


class AnaloguePin(IntEnum):
    """Analogue Pins numbering."""

    A0 = 14
    A1 = 15
    A2 = 16
    A3 = 17
    A4 = 18
    A5 = 19


PinNumber = Union[int, AnaloguePin]


class Ruggeduino(ArduinoUno):
    """Student Robotics Ruggeduino board."""

    def __init__(
            self,
            serial: str,
            backend: Backend
    ):
        super().__init__(serial, backend, name="Ruggeduino")

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of the board."""
        return self._backend.firmware_version

    def make_safe(self) -> None:
        """Make this board safe."""
        pass

    @staticmethod
    def supported_components() -> Set[Type[Component]]:
        """List the types of components supported by this board."""
        return {
            GPIOPin,
            LED,
        }
