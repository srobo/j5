"""Classes for the SR v4 Power Board."""

from typing import TYPE_CHECKING, List

from j5.backends import Backend, Environment
from j5.boards import Board

if TYPE_CHECKING:
    from j5.components import Component  # noqa
    from typing import Type  # noqa

class PowerBoard(Board):
    """Student Robotics v4 Power Board."""

    def __init__(self, serial: str, environment: Environment):
        self._serial = serial
        self._environment = environment

        self._backend = self._environment.get_backend(self.__class__)

    @property
    def name(self) -> str:
        """Get a human friendly name for this board."""
        return "Student Robotics v4 Power Board"

    @property
    def serial(self) -> str:
        """Get the serial numeber."""
        return self._serial

    def make_safe(self) -> None:
        """Make this board safe."""
        pass

    @staticmethod
    def supported_components() -> List['Type[Component]']:
        """List the types of components supported by this board."""
        return []

    @staticmethod
    def discover(backend: Backend) -> List['PowerBoard']:
        """Detect all connected power boards."""
        return []
