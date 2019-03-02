"""Classes for demonstration purposes."""

from typing import TYPE_CHECKING, List, Optional, cast

from j5.backends import Backend, Environment
from j5.boards import Board
from j5.components.led import LED

if TYPE_CHECKING:
    from j5.components import Component  # noqa
    from typing import Type  # noqa
    from j5.components.led import LEDInterface  # noqa


class DemoBoard(Board):
    """A board for demo purposes, containing 3 LEDs."""

    def __init__(self, serial: str, environment: Environment):
        self._environment = environment
        self._backend = environment.get_backend(self.__class__)()
        self._serial = serial
        self._leds = [LED(n, self, cast('LEDInterface', self._backend))
                      for n in range(0, 3)]

    @property
    def name(self) -> str:
        """Get a human friendly name for this board."""
        return "Demo Board"

    @property
    def serial(self) -> str:
        """Get the serial number."""
        return self._serial

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of this board."""
        return self._backend.get_firmware_version(self)

    def make_safe(self) -> None:
        """Make this board safe."""
        pass

    @staticmethod
    def supported_components() -> List['Type[Component]']:
        """List the types of component supported by this Board."""
        return [LED]

    @staticmethod
    def discover(backend: Backend) -> List[Board]:
        """Detect all connected boards of this type and return them."""
        return [DemoBoard(str(n), backend.environment) for n in range(0, 3)]

    @property
    def leds(self) -> List[LED]:
        """Get the leds on the board."""
        return self._leds
