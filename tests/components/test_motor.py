"""Tests for the motor classes."""
from typing import Mapping

import pytest

from j5.components.motor import (
    Motor,
    MotorInterface,
    MotorSpecialState,
    MotorState,
)


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


def test_motor_interface_implementation() -> None:
    """Test that we can implement the MotorInterface."""
    MockMotorDriver()


def test_motor_interface_class() -> None:
    """Test that the interface class is MotorInterface."""
    assert Motor.interface_class() is MotorInterface


def test_motor_instantiation() -> None:
    """Test that we can instantiate a Motor."""
    Motor(0, MockMotorDriver())


def test_motor_get_state_float() -> None:
    """Test that we can get the state of a motor."""
    motor0 = Motor(0, MockMotorDriver())
    motor1 = Motor(1, MockMotorDriver())

    assert type(motor0.state) is float
    assert type(motor1.state) is float

    assert motor0.state == 0
    assert motor1.state == 0.5


def test_motor_get_state_special() -> None:
    """Test that we can get the special state of a motor."""
    motor0 = Motor(2, MockMotorDriver())
    motor1 = Motor(3, MockMotorDriver())

    assert type(motor0.state) is MotorSpecialState
    assert type(motor1.state) is MotorSpecialState

    assert motor0.state == MotorSpecialState.COAST
    assert motor1.state == MotorSpecialState.BRAKE


def test_motor_set_state() -> None:
    """Test that we can set the state of a motor."""
    motor = Motor(0, MockMotorDriver())

    motor.state = 0
    motor.state = 1
    motor.state = -1
    motor.state = 0.123

    motor.state = MotorSpecialState.COAST
    motor.state = MotorSpecialState.BRAKE


def test_motor_set_state_out_of_bounds() -> None:
    """Test that an error is thrown when the state is out of bounds."""
    motor = Motor(0, MockMotorDriver())

    with pytest.raises(ValueError):
        motor.state = 1.1

    with pytest.raises(ValueError):
        motor.state = -1.2
