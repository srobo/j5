"""Tests for the servo classes."""
from typing import List, Optional, Type

import pytest

from j5.boards import Board
from j5.components.servo import Servo, ServoInterface, ServoPosition


class MockServoDriver(ServoInterface):
    """A testing driver for servos."""

    def get_servo_position(self, identifier: int) -> ServoPosition:
        """Get the position of a Servo."""
        return 0.5

    def set_servo_position(
            self,
            identifier: int,
            position: ServoPosition,
    ) -> None:
        """Set the position of a Servo."""
        pass


class MockServoBoard(Board):
    """A testing board for servos."""

    def __init__(self) -> None:
        pass

    @property
    def name(self) -> str:
        """The name of this board."""
        return "Testing Servo Board"

    @property
    def serial(self) -> str:
        """The serial number of this board."""
        return "SERIAL"

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of this board."""
        return None

    @staticmethod
    def supported_components() -> List[Type["Component"]]:
        """List the types of component that this Board supports."""
        return [Servo]

    def make_safe(self) -> None:
        """Make this board safe."""
        pass


def test_servo_interface_implementation() -> None:
    """Test that we can implement the ServoInterface."""
    MockServoDriver()


def test_servo_interface_class() -> None:
    """Test that the interface class is ServoInterface."""
    assert Servo.interface_class() is ServoInterface


def test_servo_instantiation() -> None:
    """Test that we can instantiate a Servo."""
    Servo(0, MockServoBoard(), MockServoDriver())


def test_servo_get_position() -> None:
    """Test that we can get the position of a servo."""
    servo = Servo(2, MockServoBoard(), MockServoDriver())
    assert type(servo.position) is float
    assert servo.position == 0.5


def test_servo_set_position() -> None:
    """Test that we can set the position of a servo."""
    servo = Servo(2, MockServoBoard(), MockServoDriver())
    servo.position = 0.6


def test_servo_set_position_none() -> None:
    """Test that we can set the position of a servo to None."""
    servo = Servo(2, MockServoBoard(), MockServoDriver())
    servo.position = None


def test_servo_set_position_out_of_bounds() -> None:
    """Test that we cannot set < -1 or > 1."""
    servo = Servo(2, MockServoBoard(), MockServoDriver())

    with pytest.raises(ValueError):
        servo.position = 2

    with pytest.raises(ValueError):
        servo.position = -2
