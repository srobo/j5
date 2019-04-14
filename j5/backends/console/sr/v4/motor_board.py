"""Console Backend for the SR v4 Motor Board."""

from typing import List, Optional, Type

from j5.backends import Backend
from j5.backends.console import Console, ConsoleEnvironment
from j5.boards import Board
from j5.boards.sr.v4.motor_board import MotorBoard
from j5.components.motor import MotorInterface, MotorSpecialState, MotorState


class SRV4MotorBoardConsoleBackend(
    MotorInterface,
    Backend,
):
    """The console implementation of the SR v4 motor board."""

    environment = ConsoleEnvironment
    board = MotorBoard

    @classmethod
    def discover(cls) -> List[Board]:
        """Discover boards that this backend can control."""
        raise NotImplementedError("The Console Backend cannot discover boards.")

    def __init__(self, serial: str, console_class: Type[Console] = Console) -> None:
        self._serial = serial

        # Initialise our stored values for the state.
        self._state: List[MotorState] = [
            MotorSpecialState.BRAKE
            for _ in range(0, 2)
        ]

        # Setup console helper
        self._console = console_class(f"{self.board.__name__}({self._serial})")

    def get_firmware_version(self) -> Optional[str]:
        """The firmware version reported by the board."""
        return None  # Console, so no firmware

    def get_motor_state(self, identifier: int) -> MotorState:
        """Get the current motor state."""
        # We are unable to read the state from the motor board, in hardware
        # so instead of asking, we'll get the last set value.
        return self._state[identifier]

    def set_motor_state(self, identifier: int, power: MotorState) -> None:
        """Set the state of a motor."""
        if identifier not in range(0, 2):
            raise ValueError(
                f"Invalid motor identifier: {identifier}, valid values are: 0, 1",
            )
        self._state[identifier] = power
        self._console.info(f"Setting motor {identifier} to {power}.")
