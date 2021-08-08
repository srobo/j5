"""Console Backend for the SR v4 Servo Board."""

from typing import List, Optional, Set, Type, cast

from j5.backends import Backend
from j5.backends.console import Console
from j5.boards import Board
from j5.boards.sr.v4.servo_board import ServoBoard
from j5.components.servo import ServoInterface, ServoPosition


class SRV4ServoBoardConsoleBackend(
    ServoInterface,
    Backend,
):
    """The console implementation of the SR v4 Servo board."""

    board = ServoBoard

    @classmethod
    def discover(cls) -> Set[Board]:
        """
        Discover boards that this backend can control.

        :returns: set of boards that this backend can control.
        """
        return {cast(Board, ServoBoard("SERIAL", cls("SERIAL")))}

    def __init__(self, serial: str, console_class: Type[Console] = Console) -> None:
        self._serial = serial

        # Initialise our stored values for the positions.
        self._positions: List[ServoPosition] = [None for _ in range(0, 12)]

        # Setup console helper
        self._console = console_class(f"{self.board.__name__}({self._serial})")

    @property
    def serial(self) -> str:
        """
        The serial number reported by the board.

        :returns: serial number reported by the board.
        """
        return self._serial

    @property
    def firmware_version(self) -> Optional[str]:
        """
        The firmware version reported by the board.

        :returns: firmware version reported by the board, if any.
        """
        return None  # Console, so no firmware

    def get_servo_position(self, identifier: int) -> ServoPosition:
        """
        Get the servo position.

        :param identifier: Port of servo to check.
        :returns: Position of servo.
        """
        # We are unable to read the state from the servo board, in hardware
        # so instead of asking, we'll get the last set value.
        return self._positions[identifier]

    def set_servo_position(self, identifier: int, position: ServoPosition) -> None:
        """
        Set the servo position.

        :param identifier: Port of servo to set position.
        :param position: Position to set the servo to.
        :raises ValueError: Unknown servo identifier.
        """
        if identifier not in range(0, 12):
            raise ValueError(
                f"Invalid servo identifier: {identifier}, valid values are: 0 - 11",
            )
        self._positions[identifier] = position
        if position is None:
            position_human_name = "unpowered"
        else:
            position_human_name = str(position)
        self._console.info(f"Setting servo {identifier} to {position_human_name}.")
