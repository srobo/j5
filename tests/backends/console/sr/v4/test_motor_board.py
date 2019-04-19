"""Tests for the SRv4 Motor Board console backend."""

import pytest
from tests.backends.console.helpers import MockConsole

from j5.backends.console.sr.v4.motor_board import SRV4MotorBoardConsoleBackend
from j5.components.motor import MotorSpecialState


def test_backend_initialisation() -> None:
    """Test that we can initialise a Backend."""
    backend = SRV4MotorBoardConsoleBackend("Test")
    assert type(backend) is SRV4MotorBoardConsoleBackend

    assert len(backend._state) == 2
    # Check initially all BRAKE.
    assert all(state == MotorSpecialState.BRAKE for state in backend._state)


def test_backend_discover() -> None:
    """
    Test that the backend can not discover boards.

    This backend does not support discovery.
    """
    with pytest.raises(NotImplementedError):
        SRV4MotorBoardConsoleBackend.discover()


def test_backend_firmware_version() -> None:
    """Test that we can get the firmware version."""
    backend = SRV4MotorBoardConsoleBackend("TestBoard")

    assert backend.firmware_version is None


def test_backend_serial_number() -> None:
    """Test that we can get the serial number."""
    backend = SRV4MotorBoardConsoleBackend("TestBoard")

    assert backend.serial == "TestBoard"


def test_backend_get_motor_state() -> None:
    """Test that we can get the motor states."""
    backend = SRV4MotorBoardConsoleBackend("TestBoard")

    for i in range(0, 2):
        assert backend.get_motor_state(i) == MotorSpecialState.BRAKE
        backend._state[i] = 0.0
        assert backend.get_motor_state(i) == 0.0
        backend._state[i] = -1
        assert backend.get_motor_state(i) == -1


def test_backend_set_motor_state() -> None:
    """Test that we can set the motor states."""
    backend = SRV4MotorBoardConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._console.expects = "Setting motor 0 to 0.5."  # type: ignore
    backend.set_motor_state(0, 0.5)

    backend._console.expects = "Setting motor 0 to 1.0."  # type: ignore
    backend.set_motor_state(0, 1.0)

    backend._console.expects = "Setting motor 0 to -1.0."  # type: ignore
    backend.set_motor_state(0, -1.0)

    backend._console.expects = "Setting motor 0 to BRAKE."  # type: ignore
    backend.set_motor_state(0, MotorSpecialState.BRAKE)

    backend._console.expects = "Setting motor 0 to COAST."  # type: ignore
    backend.set_motor_state(0, MotorSpecialState.COAST)


def test_backend_set_motor_state_out_of_range() -> None:
    """Test that we throw an error if the value is out of range."""
    backend = SRV4MotorBoardConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )
    with pytest.raises(ValueError):
        backend._console.expects = "Setting motor 10 to -1.0."  # type: ignore
        backend.set_motor_state(10, -1.0)
