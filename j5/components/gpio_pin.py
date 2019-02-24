"""Classes for GPIO Pins."""

from enum import IntEnum
from typing import List, Type

from j5.boards import Board
from j5.components import Component, Interface


class GPIOPinMode(IntEnum):
    """Hardware modes that a GPIO pin can be set to."""

    DIGITAL_INPUT = 0  # The digital state of the pin can be read
    DIGITAL_INPUT_PULLUP = 1  # Same as DIGITAL_INPUT but the internal pull-up is enabled
    DIGITAL_OUTPUT = 2  # The digital state of the pin can be set.

    ANALOGUE_INPUT = 3  # The analogue voltage of the pin can be read.
    ANALOGUE_OUTPUT = 4  # The analogue voltage of the pin can be set using a DAC.

    PWM_OUTPUT = 5  # A PWM output signal can be created on the pin.


class GPIOPinInterface(Interface):
    """An interface containing the methods required for a GPIO Pin."""

    pass


class GPIOPin(Component):
    """A GPIO Pin."""

    def __init__(
            self,
            identifier: int,
            board: Board,
            backend: GPIOPinInterface,
            supported_modes: List[GPIOPinMode] = [],
    ) -> None:
        self._board = board
        self._backend = backend
        self._identifier = identifier
        self._supported_modes = supported_modes

    @staticmethod
    def interface_class() -> Type[GPIOPinInterface]:
        """Get the interface class that is required to use this component."""
        return GPIOPinInterface
