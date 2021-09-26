"""Classes for the SR v4 Servo Board."""
from typing import Optional, Set, Type, cast

from j5.backends import Backend
from j5.boards import Board
from j5.components import Component, Servo, ServoInterface
from j5.types import ImmutableList


class ServoBoard(Board):
    """Student Robotics v4 Servo Board."""

    name: str = "Student Robotics v4 Servo Board"

    def __init__(self, serial: str, backend: Backend):
        self._serial = serial
        self._backend = backend

        self._servos = ImmutableList[Servo](
            Servo(servo, cast(ServoInterface, self._backend))
            for servo in range(0, 12)
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

    def make_safe(self) -> None:
        """
        Make this board safe.

        It is safest to leave the servos where they are, so do nothing.
        """
        pass

    @staticmethod
    def supported_components() -> Set[Type[Component]]:
        """
        List the types of components supported by this board.

        :returns: Set of components supported by the board.
        """
        return {Servo}

    @property
    def servos(self) -> ImmutableList[Servo]:
        """
        Get the servos on this board.

        :returns: List of servos on the board.
        """
        return self._servos
