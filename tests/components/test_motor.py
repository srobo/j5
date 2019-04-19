"""Tests for the motor classes."""
from typing import TYPE_CHECKING, Mapping, Optional, Set, Type

import pytest

from j5.boards import Board
from j5.components.motor import (
    Motor,
    MotorInterface,
    MotorSpecialState,
    MotorState,
)

if TYPE_CHECKING:
    from j5.components import Component  # noqa


class MockMotorDriver(MotorInterface):
    """A testing driver for motors."""

    def get_motor_state(self, identifier: int) -> MotorState:
        """
        Get the state of the motor.

        As this is a testing function, the state is actually dependent on the identifier.
        """
        test_states: Mapping[int, MotorState] = {
            0: 0.0,
            1: 0.5,
            2: MotorSpecialState.COAST,
            3: MotorSpecialState.BRAKE,
        }
        return test_states[identifier]

    def set_motor_state(self, identifier: int, power: MotorState) -> None:
        """Set the state of the motor."""
        pass


class MockMotorBoard(Board):
    """A testing board for motors."""

    def __init__(self) -> None:
        pass

    @property
    def name(self) -> str:
        """The name of this board."""
        return "Testing Motor Board"

    @property
    def serial(self) -> str:
        """The serial number of this board."""
        return "SERIAL"

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of this board."""
        return None

    @staticmethod
    def supported_components() -> Set[Type["Component"]]:
        """List the types of component that this Board supports."""
        return {Motor}

    def make_safe(self) -> None:
        """Make this board safe."""
        pass


def test_motor_interface_implementation() -> None:
    """Test that we can implement the MotorInterface."""
    MockMotorDriver()


def test_motor_interface_class() -> None:
    """Test that the interface class is MotorInterface."""
    assert Motor.interface_class() is MotorInterface


def test_motor_instantiation() -> None:
    """Test that we can instantiate a Motor."""
    Motor(0, MockMotorBoard(), MockMotorDriver())


def test_motor_get_state_float() -> None:
    """Test that we can get the state of a motor."""
    motor0 = Motor(0, MockMotorBoard(), MockMotorDriver())
    motor1 = Motor(1, MockMotorBoard(), MockMotorDriver())

    assert type(motor0.state) is float
    assert type(motor1.state) is float

    assert motor0.state == 0
    assert motor1.state == 0.5


def test_motor_get_state_special() -> None:
    """Test that we can get the special state of a motor."""
    motor0 = Motor(2, MockMotorBoard(), MockMotorDriver())
    motor1 = Motor(3, MockMotorBoard(), MockMotorDriver())

    assert type(motor0.state) is MotorSpecialState
    assert type(motor1.state) is MotorSpecialState

    assert motor0.state == MotorSpecialState.COAST
    assert motor1.state == MotorSpecialState.BRAKE


def test_motor_set_state() -> None:
    """Test that we can set the state of a motor."""
    motor = Motor(0, MockMotorBoard(), MockMotorDriver())

    motor.state = 0
    motor.state = 1
    motor.state = -1
    motor.state = 0.123

    motor.state = MotorSpecialState.COAST
    motor.state = MotorSpecialState.BRAKE


def test_motor_set_state_out_of_bounds() -> None:
    """Test that an error is thrown when the state is out of bounds."""
    motor = Motor(0, MockMotorBoard(), MockMotorDriver())

    with pytest.raises(ValueError):
        motor.state = 1.1

    with pytest.raises(ValueError):
        motor.state = -1.2
