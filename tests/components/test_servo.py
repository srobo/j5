"""Tests for the servo classes."""
from typing import List, Type

import pytest

from j5.backends import Backend
from j5.boards import Board
from j5.components.servo import Servo, ServoInterface, ServoPosition


class MockServoDriver(ServoInterface):
    """A testing driver for servos."""

    def get_servo_position(self, board: Board, identifier: int) -> ServoPosition:
        """Get the position of a Servo."""
        return 0.5

    def set_servo_position(
            self,
            board: Board,
            identifier: int,
            position: ServoPosition,
    ) -> None:
        """Set the position of a Servo."""
        pass


class MockServoBoard(Board):
    """A testing board for servos."""

    @property
    def name(self) -> str:
        """The name of this board."""
        return "Testing Servo Board"

    @property
    def serial(self) -> str:
        """The serial number of this board."""
        return "SERIAL"

    @property
    def supported_components(self) -> List[Type["Component"]]:
        """List the types of component that this Board supports."""
        return [Servo]

    def make_safe(self):
        """Make this board safe."""
        pass

    @staticmethod
    def discover(backend: Backend):
        """Detect all of the boards on a given backend."""
        return []


def test_servo_interface_implementation():
    """Test that we can implement the ServoInterface."""
    MockServoDriver()


def test_servo_interface_class():
    """Test that the interface class is ServoInterface."""
    assert Servo.interface_class() is ServoInterface


def test_servo_instantiation():
    """Test that we can instantiate a Servo."""
    Servo(0, MockServoBoard(), MockServoDriver())


def test_servo_get_position():
    """Test that we can get the position of a servo."""
    servo = Servo(2, MockServoBoard(), MockServoDriver())
    assert type(servo.position) is float
    assert servo.position == 0.5


def test_servo_set_position():
    """Test that we can set the position of a servo."""
    servo = Servo(2, MockServoBoard(), MockServoDriver())
    servo.position = 0.6


def test_servo_set_position_out_of_bounds():
    """Test that we cannot set < -1 or > 1."""
    servo = Servo(2, MockServoBoard(), MockServoDriver())

    with pytest.raises(ValueError):
        servo.position = 2

    with pytest.raises(ValueError):
        servo.position = -2
