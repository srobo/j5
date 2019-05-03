"""Tests for the SR v4 Servo Board console backend."""

import pytest
from tests.backends.console.helpers import MockConsole

from j5.backends.console.sr.v4.servo_board import SRV4ServoBoardConsoleBackend


def test_backend_initialisation() -> None:
    """Test that we can initialise a Backend."""
    backend = SRV4ServoBoardConsoleBackend("Test")
    assert type(backend) is SRV4ServoBoardConsoleBackend

    assert len(backend._positions) == 12

    # Check initially all None.
    assert all(pos is None for pos in backend._positions)


def test_backend_discover() -> None:
    """
    Test that the backend can not discover boards.

    This backend does not support discovery.
    """
    with pytest.raises(NotImplementedError):
        SRV4ServoBoardConsoleBackend.discover()


def test_backend_firmware_version() -> None:
    """Test that we can get the firmware version."""
    backend = SRV4ServoBoardConsoleBackend("TestBoard")

    assert backend.firmware_version is None


def test_backend_serial_number() -> None:
    """Test that we can get the serial number."""
    backend = SRV4ServoBoardConsoleBackend("TestBoard")

    assert backend.serial == "TestBoard"


def test_backend_set_servo_pos() -> None:
    """Test the we can get the servo positions."""
    backend = SRV4ServoBoardConsoleBackend("TestBoard")

    for i in range(0, 12):
        assert backend.get_servo_position(i) is None
        backend._positions[i] = 0.0
        assert backend.get_servo_position(i) == 0.0
        backend._positions[i] = -1.0
        assert backend.get_servo_position(i) == -1.0


def test_backend_get_servo_pos() -> None:
    """Test that we can set the servo positions."""
    backend = SRV4ServoBoardConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._console.expects = "Setting servo 0 to 0.5."  # type: ignore
    backend.set_servo_position(0, 0.5)

    backend._console.expects = "Setting servo 1 to 1.0."  # type: ignore
    backend.set_servo_position(1, 1.0)

    backend._console.expects = "Setting servo 2 to -1.0."  # type: ignore
    backend.set_servo_position(2, -1.0)

    backend._console.expects = "Setting servo 3 to unpowered."  # type: ignore
    backend.set_servo_position(3, None)


def test_backend_set_servo_pos_out_of_range() -> None:
    """Test that we throw an error if the value is out of range."""
    backend = SRV4ServoBoardConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )
    with pytest.raises(ValueError):
        backend._console.expects = "Setting servo 10 to -1.0."  # type: ignore
        backend.set_servo_position(18, -1.0)
