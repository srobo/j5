"""Console Backend for the SR v4 Motor Board."""

from typing import List, Optional, Set, Type, cast

from j5.backends import Backend
from j5.backends.console import Console
from j5.boards import Board
from j5.boards.sr.v4.motor_board import MotorBoard
from j5.components.motor import MotorInterface, MotorSpecialState, MotorState


class SRV4MotorBoardConsoleBackend(
    MotorInterface,
    Backend,
):
    """The console implementation of the SR v4 motor board."""

    board = MotorBoard

    @classmethod
    def discover(cls) -> Set[Board]:
        """
        Discover boards that this backend can control.

        :returns: set of boards that this backend can control.
        """
        return {cast(Board, MotorBoard("SERIAL", cls("SERIAL")))}

    def __init__(self, serial: str, console_class: Type[Console] = Console) -> None:
        self._serial = serial

        # Initialise our stored values for the state.
        self._state: List[MotorState] = [
            MotorSpecialState.BRAKE
            for _ in range(0, 2)
        ]

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

    def get_motor_state(self, identifier: int) -> MotorState:
        """
        Get the current motor state.

        :param identifier: identifier of the motor
        :returns: state of the motor.
        """
        # We are unable to read the state from the motor board, in hardware
        # so instead of asking, we'll get the last set value.
        return self._state[identifier]

    def set_motor_state(self, identifier: int, power: MotorState) -> None:
        """
        Set the state of a motor.

        :param identifier: identifier of the motor
        :param power: state of the motor.
        :raises ValueError: invalid motor identifier.
        """
        if identifier not in range(0, 2):
            raise ValueError(
                f"Invalid motor identifier: {identifier}, valid values are: 0, 1",
            )
        self._state[identifier] = power
        if isinstance(power, MotorSpecialState):
            power_human_name = power.name
        else:
            power_human_name = str(power)
        self._console.info(f"Setting motor {identifier} to {power_human_name}.")
