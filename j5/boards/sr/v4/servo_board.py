"""Classes for the SR v4 Servo Board."""
from typing import TYPE_CHECKING, List, Optional, Set, Type, cast

from j5.backends import Backend
from j5.boards import Board
from j5.components.servo import Servo, ServoInterface

if TYPE_CHECKING:  # pragma: no cover
    from j5.components import (  # noqa: F401
        Component,
    )


class ServoBoard(Board):
    """Student Robotics v4 Servo Board."""

    name: str = "Student Robotics v4 Servo Board"

    def __init__(self, serial: str, backend: Backend):
        self._serial = serial
        self._backend = backend

        self._servos: List[Servo] = [
            Servo(servo, cast(ServoInterface, self._backend))
            for servo in range(0, 12)
        ]

    @property
    def serial(self) -> str:
        """Get the serial number."""
        return self._serial

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
    def supported_components() -> Set[Type['Component']]:
        """List the types of components supported by this board."""
        return {Servo}

    @property
    def servos(self) -> List[Servo]:
        """Get the servos on this board."""
        return self._servos
