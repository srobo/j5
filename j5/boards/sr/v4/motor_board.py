"""Classes for the SR v4 Motor Board."""
from typing import TYPE_CHECKING, List, Optional, Set, Type, cast

from j5.backends import Backend
from j5.boards import Board
from j5.components import (
    Motor,
    MotorInterface,
    MotorSpecialState,
    SerialNumberInterface,
)

if TYPE_CHECKING:  # pragma: no cover
    from j5.components import Interface  # noqa: F401


class MotorBoard(Board):
    """Student Robotics v4 Motor Board."""

    name: str = "Student Robotics v4 Motor Board"

    def __init__(self, backend: Backend):
        self._backend = backend

        self._outputs: List[Motor] = [
            Motor(output, cast(MotorInterface, self._backend))
            for output in range(0, 2)
        ]

    @property
    def serial(self) -> str:
        """Get the serial number."""
        return cast("SerialNumberInterface", self._backend).get_serial_number()

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of the board."""
        return self._backend.firmware_version

    @property
    def motors(self) -> List[Motor]:
        """Get the motors on this board."""
        return self._outputs

    def make_safe(self) -> None:
        """Make this board safe."""
        for output in self._outputs:
            # Brake both motors.
            output.power = MotorSpecialState.BRAKE

    @staticmethod
    def required_interfaces() -> Set[Type["Interface"]]:
        """The interfaces that a backend for this board must implement."""
        return {MotorInterface, SerialNumberInterface}
