"""Classes for demonstration purposes."""

from typing import List

from j5 import Board

from j5.components.led import LED
from j5.backends import Backend


class DemoBoard(Board):
    """A board for demo purposes, containg 3 LEDs."""

    def __init__(self, backend: Backend):
        self._backend = backend()
        self._leds = [
            LED(n, self._backend)
            for n in range(0, 3)
        ]

    @property
    def leds(self) -> List[LED]:
        return self._leds
