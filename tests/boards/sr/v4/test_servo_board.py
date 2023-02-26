"""Tests for the SR v4 Servo Board."""

import pytest

from j5.backends import Backend
from j5.boards import Board
from j5.boards.sr.v4 import ServoBoard
from j5.components.servo import Servo, ServoInterface, ServoPosition


class MockServoBoardBackend(ServoInterface, Backend):
    """A mock servo board backend implementation."""

    board = ServoBoard

    @classmethod
    def discover(cls) -> set[Board]:
        """Discover the Servo Boards on this backend."""
        return set()

    def __init__(self) -> None:
        self._positions: list[ServoPosition] = [
            None
            for _ in range(0, 12)
        ]

    @property
    def firmware_version(self) -> str | None:
        """The firmware version of the board."""
        return None

    def get_servo_position(self, identifier: int) -> ServoPosition:
        """Get the position of a servo."""
        return self._positions[identifier]

    def set_servo_position(self, identifier: int, position: ServoPosition) -> None:
        """Set the position of a servo."""
        self._positions[identifier] = position


def test_servo_board_supported_components() -> None:
    """Test the supported components on the servo board."""
    assert ServoBoard.supported_components() == {Servo}


def test_servo_board_discover() -> None:
    """Test that we can discover servo boards."""
    assert MockServoBoardBackend.discover() == set()


def test_servo_board_instantiation() -> None:
    """Test that we can instantiate a servo board."""
    ServoBoard("SERIAL0", MockServoBoardBackend())


def test_servo_board_name() -> None:
    """Test the name attribute of the servo board."""
    sb = ServoBoard("SERIAL0", MockServoBoardBackend())

    assert sb.name == "Student Robotics v4 Servo Board"


def test_servo_board_firmware_version() -> None:
    """Test the firmware version on the servo board."""
    sb = ServoBoard("SERIAL0", MockServoBoardBackend())

    assert sb.firmware_version is None


def test_servo_board_serial_number() -> None:
    """Test the serial attribute of the servo board."""
    sb = ServoBoard("SERIAL0", MockServoBoardBackend())

    assert sb.serial_number == "SERIAL0"


def test_servo_board_make_safe() -> None:
    """Test the make_safe method of the servo board."""
    sb = ServoBoard("SERIAL0", MockServoBoardBackend())

    sb.make_safe()


def test_servo_board_servos() -> None:
    """Test the servos on the servo board."""
    sb = ServoBoard("SERIAL0", MockServoBoardBackend())

    assert all(type(s) is Servo for s in sb.servos)


def test_servo_mutability() -> None:
    """
    Test the mutability of Servos.

    Ensures that Servo objects cannot be lost.
    """
    sb = ServoBoard("SERIAL0", MockServoBoardBackend())

    with pytest.raises(TypeError):
        sb.servos[1] = 0.5  # type: ignore
