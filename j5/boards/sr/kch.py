"""Board definition for the Student Robotics KCH."""

from enum import Enum
from typing import Dict, Set, Type, cast

from j5.backends import Backend
from j5.boards import Board
from j5.components import RGBLED, Component, RGBLEDInterface


class KCHLED(Enum):
    """A mapping of name to identifier for the KCH RGB LEDs."""

    A = 0
    B = 1
    C = 2
    START = 3


class KCHBoard(Board):
    """Student Robotics KCH v1 Rev A & Rev B."""

    name: str = "Student Robotics KCH v1"

    def __init__(self, serial: str, backend: Backend):
        self._serial = serial
        self._backend = backend

        self._leds = {
            led: RGBLED(led.value, cast("RGBLEDInterface", self._backend))
            for led in KCHLED
        }

    @property
    def serial_number(self) -> str:
        """
        Get the serial number of the board.

        :returns: Serial number of the board.
        """
        return self._serial

    @property
    def firmware_version(self) -> None:
        """
        Get the firmware version of the board.

        The KCH does not have firmware.

        :returns: Firmware version of the board.
        """
        return None

    def make_safe(self) -> None:
        """Make this board safe."""
        pass

    @property
    def leds(self) -> Dict[KCHLED, RGBLED]:
        """
        The RGB LEDs on the KCH.

        :returns: A dictionary of LED name to component.
        """
        return self._leds

    @property
    def a(self) -> RGBLED:
        """
        The A RGB LED.

        :returns: The component to control RGB LED A.
        """
        return self.leds[KCHLED.A]

    @property
    def b(self) -> RGBLED:
        """
        The B RGB LED.

        :returns: The component to control RGB LED B.
        """
        return self.leds[KCHLED.B]

    @property
    def c(self) -> RGBLED:
        """
        The C RGB LED.

        :returns: The component to control RGB LED C.
        """
        return self.leds[KCHLED.C]

    @staticmethod
    def supported_components() -> Set[Type[Component]]:
        """
        List the types of components supported by this board.

        :returns: Set of components supported by the board.
        """
        return {RGBLED}
