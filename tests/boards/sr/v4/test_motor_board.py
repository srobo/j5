"""Tests for the SR v4 Motor Board."""
from typing import List, Optional, Set

from j5.backends import Backend, Environment
from j5.boards import Board
from j5.boards.sr.v4 import MotorBoard
from j5.components import (
    Motor,
    MotorInterface,
    MotorSpecialState,
    MotorState,
    SerialNumberInterface,
)

MockEnvironment = Environment("MockEnvironment")


class MockMotorBoardBackend(MotorInterface, SerialNumberInterface, Backend):
    """A mock motor board backend implementation."""

    environment = MockEnvironment
    board = MotorBoard

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover the Motor Boards on this backend."""
        return set()

    def __init__(self) -> None:
        self._states: List[MotorState] = [
            MotorSpecialState.BRAKE
            for _ in range(0, 2)
        ]

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return None

    def get_motor_state(self, identifier: int) -> MotorState:
        """Get the current state of a motor."""
        return self._states[identifier]

    def set_motor_state(self, identifier: int, power: MotorState) -> None:
        """Set the current state of a motor."""
        self._states[identifier] = power

    def get_serial_number(self) -> str:
        """Get the board's serial number."""
        return "SERIAL0"


def test_motor_board_required_interfaces() -> None:
    """Test the required interfaces on the motor board."""
    assert MotorBoard.required_interfaces() == {MotorInterface, SerialNumberInterface}


def test_motor_board_discover() -> None:
    """Test that we can discover motor boards."""
    assert MockMotorBoardBackend.discover() == set()


def test_motor_board_instantiation() -> None:
    """Test that we can instantiate a Motor Board."""
    MotorBoard(MockMotorBoardBackend())


def test_motor_board_firmware_version() -> None:
    """Test the firmware version on the motor board."""
    mb = MotorBoard(MockMotorBoardBackend())

    assert mb.firmware_version is None


def test_motor_board_name() -> None:
    """Test the name attribute of the motor board."""
    mb = MotorBoard(MockMotorBoardBackend())

    assert mb.name == "Student Robotics v4 Motor Board"


def test_motor_board_serial() -> None:
    """Test the serial attribute of the motor board."""
    mb = MotorBoard(MockMotorBoardBackend())

    assert mb.serial == "SERIAL0"


def test_motor_board_make_safe() -> None:
    """Test the make_safe method of the motor board."""
    mb = MotorBoard(MockMotorBoardBackend())

    for m in mb.motors:
        m.power = 1

    mb.make_safe()

    for m in mb.motors:
        assert m.power == MotorSpecialState.BRAKE


def test_motor_board_motors() -> None:
    """Test the motor_outputs on the motor board."""
    mb = MotorBoard(MockMotorBoardBackend())

    for m in mb.motors:
        assert type(m) is Motor
