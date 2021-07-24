"""
Classes for the Student Robotics Ruggeduino.

It's similar to the Sourcebots Arduino, but without official ultrasound support.
"""
from typing import Set, Type, cast

from j5.backends import Backend
from j5.boards.arduino.uno import ArduinoUno
from j5.components import (
    LED,
    Component,
    GPIOPin,
    StringCommandComponent,
    StringCommandComponentInterface,
)


class Ruggeduino(ArduinoUno):
    """Student Robotics Ruggeduino board."""

    name: str = "Ruggeduino"

    def __init__(
            self,
            serial: str,
            backend: Backend,
    ):
        super().__init__(serial, backend)

        self.command = StringCommandComponent(
            0,
            cast(StringCommandComponentInterface, self._backend),
        )

    @staticmethod
    def supported_components() -> Set[Type[Component]]:
        """
        List the types of components supported by this board.

        :returns: Set of components supported by the board.
        """
        return {
            GPIOPin,
            LED,
            StringCommandComponent,
        }
