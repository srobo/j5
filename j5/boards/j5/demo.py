"""Classes for demonstration purposes."""

from typing import List

from j5 import Board
from j5.backends import BackendGroup
from j5.components.led import LED


class DemoBoard(Board):
    """A board for demo purposes, containng 3 LEDs."""

    def __init__(self, backend_group: BackendGroup):
        self._backend = backend_group.get_backend(self.__class__)
        self._leds = [LED(n, self._backend) for n in range(0, 3)]

    @property
    def leds(self) -> List[LED]:
        """Get the leds on the board."""
        return self._leds
