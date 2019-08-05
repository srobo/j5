"""Classes for the SR v4 Servo Board."""
from typing import TYPE_CHECKING, List, Optional, Set, Type, cast

from j5.backends import Backend
from j5.boards import Board
from j5.components import SerialNumberInterface, Servo, ServoInterface

if TYPE_CHECKING:  # pragma: no cover
    from j5.components import Interface  # noqa: F401


class ServoBoard(Board):
    """Student Robotics v4 Servo Board."""

    name: str = "Student Robotics v4 Servo Board"

    def __init__(self, backend: Backend):
        self._backend = backend

        self._servos: List[Servo] = [
            Servo(servo, cast(ServoInterface, self._backend))
            for servo in range(0, 12)
        ]

    @property
    def serial(self) -> str:
        """Get the serial number."""
        return cast("SerialNumberInterface", self._backend).get_serial_number()

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of the board."""
        return self._backend.firmware_version

    def make_safe(self) -> None:
        """
        Make this board safe.

        It is safest to leave the servos where they are, so do nothing.
        """
        pass

    @staticmethod
    def required_interfaces() -> Set[Type["Interface"]]:
        """The interfaces that a backend for this board must implement."""
        return {ServoInterface, SerialNumberInterface}

    @property
    def servos(self) -> List[Servo]:
        """Get the servos on this board."""
        return self._servos
