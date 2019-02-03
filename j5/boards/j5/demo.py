"""Classes for demonstration purposes."""

from typing import Any, List

from j5.backends import Backend, Environment
from j5.boards import Board
from j5.components.led import LED


class DemoBoard(Board):
    """A board for demo purposes, containing 3 LEDs."""

    def __init__(self, serial: str, environment: Environment):
        self._backend = environment.get_backend(self.__class__)
        self._serial = serial
        self._leds = [LED(n, self, self._backend) for n in range(0, 3)]  # type: ignore

    @property
    def name(self) -> str:
        """Get a human friendly name for this board."""
        return "Demo Board"

    @property
    def serial(self) -> str:
        """Get the serial number."""
        return self._serial

    @staticmethod
    def supported_components():
        """List the components that this Board supports."""
        return[LED]

    @staticmethod
    def discover(backend: Backend) -> List[Any]:
        """Detect all connected boards of this type and return them."""
        return [DemoBoard(str(n), backend) for n in range(0, 3)]  # type: ignore

    @property
    def leds(self) -> List[LED]:
        """Get the leds on the board."""
        return self._leds
