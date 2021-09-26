"""Classes for the SR v4 Motor Board."""
from typing import Optional, Set, Type, cast

from j5.backends import Backend
from j5.boards import Board
from j5.components.motor import (
    Component,
    Motor,
    MotorInterface,
    MotorSpecialState,
    MotorState,
)
from j5.types import ImmutableList


class MotorBoard(Board):
    """Student Robotics v4 Motor Board."""

    name: str = "Student Robotics v4 Motor Board"

    def __init__(
            self,
            serial: str,
            backend: Backend,
            *,
            safe_state: MotorState = MotorSpecialState.BRAKE,
    ):
        self._serial = serial
        self._backend = backend
        self._safe_state = safe_state

        self._outputs = ImmutableList[Motor](
            Motor(output, cast(MotorInterface, self._backend))
            for output in range(0, 2)
        )

    @property
    def serial_number(self) -> str:
        """
        Get the serial number of the board.

        :returns: Serial number of the board.
        """
        return self._serial

    @property
    def firmware_version(self) -> Optional[str]:
        """
        Get the firmware version of the board.

        :returns: Firmware version of the board.
        """
        return self._backend.firmware_version

    @property
    def motors(self) -> ImmutableList[Motor]:
        """
        Get the motors on this board.

        :returns: List of motors attached to the board.
        """
        return self._outputs

    def make_safe(self) -> None:
        """Make this board safe."""
        for output in self._outputs:
            # Put both motors in the safe state.
            output.power = self._safe_state

    @staticmethod
    def supported_components() -> Set[Type[Component]]:
        """
        List the types of components supported by this board.

        :returns: Set of components supported by the board.
        """
        return {Motor}
