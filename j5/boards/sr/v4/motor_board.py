"""Classes for the SR v4 Motor Board."""
from typing import TYPE_CHECKING, List, Mapping, Optional, Type, cast

from j5.backends import Backend
from j5.boards import Board
from j5.components import Motor
from j5.components.motor import MotorSpecialState

if TYPE_CHECKING:  # pragma: no cover
    from j5.components import (  # noqa: F401
        MotorInterface,
        Component,
    )


class MotorBoard(Board):
    """Student Robotics v4 Motor Board."""

    def __init__(self, serial: str, backend: Backend):
        self._serial = serial
        self._backend = backend

        self._outputs: Mapping[int, Motor] = {
            output: Motor(output, self, cast(MotorInterface, self._backend))
            for output in range(0, 2)
        }

    @property
    def name(self) -> str:
        """Get a human friendly name for this board."""
        return "Student Robotics v4 Motor Board"

    @property
    def serial(self) -> str:
        """Get the serial number."""
        return self._serial

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of the board."""
        return self._backend.get_firmware_version()

    def make_safe(self) -> None:
        """Make this board safe."""
        for output in self._outputs.values():
            # Brake both motors.
            output.state = MotorSpecialState.BRAKE

    @staticmethod
    def supported_components() -> List[Type['Component']]:
        """List the types of components supported by this board."""
        return [Motor]
