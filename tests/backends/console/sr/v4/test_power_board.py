"""Test the SR v4 PowerBoard backend and associated classes."""

from datetime import timedelta

import pytest
from tests.backends.console.helpers import MockConsole

from j5.backends.console.sr.v4.power_board import SRV4PowerBoardConsoleBackend
from j5.components.piezo import Note


def test_backend_initialisation() -> None:
    """Test that we can initialise a Backend."""
    backend = SRV4PowerBoardConsoleBackend("Test")
    assert type(backend) is SRV4PowerBoardConsoleBackend

    assert len(backend._output_states) == 6
    assert not any(backend._output_states.values())  # Check initially all false.

    assert len(backend._led_states) == 2
    assert not any(backend._led_states.values())  # Check initially all false.


def test_backend_discover() -> None:
    """
    Test that the backend can not discover boards.

    This backend does not support discovery.
    """
    with pytest.raises(NotImplementedError):
        SRV4PowerBoardConsoleBackend.discover()


def test_backend_firmware_version() -> None:
    """Test that we can get the firmware version."""
    backend = SRV4PowerBoardConsoleBackend("TestBoard")

    assert backend.firmware_version is None


def test_backend_serial_number() -> None:
    """Test that we can get the serial number."""
    backend = SRV4PowerBoardConsoleBackend("TestBoard")

    assert backend.serial == "TestBoard"


def test_backend_get_power_output_enabled() -> None:
    """Test that we can read the enable status of a PowerOutput."""
    backend = SRV4PowerBoardConsoleBackend("TestBoard")

    for i in range(0, 6):
        assert not backend.get_power_output_enabled(i)

    with pytest.raises(ValueError):
        backend.get_power_output_enabled(6)


def test_backend_set_power_output_enabled() -> None:
    """Test that we can read the enable status of a PowerOutput."""
    backend = SRV4PowerBoardConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    for i in range(0, 6):
        backend._console.expects = f"Setting output {i} to True"  # type: ignore
        backend.set_power_output_enabled(i, True)

    with pytest.raises(ValueError):
        backend._console.expects = "Setting output 6 to True"  # type: ignore
        backend.set_power_output_enabled(6, True)


def test_backend_get_power_output_current() -> None:
    """Test that we can read the current on a PowerOutput."""
    backend = SRV4PowerBoardConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    for i in range(0, 6):
        backend._console.next_input = "1.2"  # type: ignore
        assert 1.2 == backend.get_power_output_current(i)

    with pytest.raises(ValueError):
        backend.get_power_output_current(6)


def test_backend_piezo_buzz() -> None:
    """Test that we can buzz the Piezo."""
    backend = SRV4PowerBoardConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    # Buzz a Note
    backend._console.expects = "Buzzing at 2349Hz for 10000ms"  # type: ignore
    backend.buzz(0, timedelta(seconds=10), Note.D7)

    # Buzz a frequency
    backend._console.expects = "Buzzing at 100Hz for 10000ms"  # type: ignore
    backend.buzz(0, timedelta(seconds=10), 100)

    # Buzz for too long.
    with pytest.raises(ValueError):
        backend.buzz(0, timedelta(seconds=100), 10)

    # Test non-existent buzzer
    with pytest.raises(ValueError):
        backend.buzz(1, timedelta(seconds=10), 0)


def test_backend_get_button_state() -> None:
    """Test that we can get the button state."""
    backend = SRV4PowerBoardConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    assert not backend.get_button_state(0)

    with pytest.raises(ValueError):
        backend.get_button_state(1)


def test_backend_wait_start_button_pressed() -> None:
    """Test that we can wait until the start button is pressed."""
    backend = SRV4PowerBoardConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._console.expects = "Waiting for start button press."  # type: ignore
    backend._console.next_input = ""  # type: ignore

    backend.wait_until_button_pressed(0)


def test_backend_get_battery_sensor_voltage() -> None:
    """Test that we can get the battery sensor voltage."""
    backend = SRV4PowerBoardConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._console.next_input = "0.982"  # type: ignore
    assert backend.get_battery_sensor_voltage(0) == 0.982

    with pytest.raises(ValueError):
        backend.get_battery_sensor_voltage(1)


def test_backend_get_battery_sensor_current() -> None:
    """Test that we can get the battery sensor current."""
    backend = SRV4PowerBoardConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    backend._console.next_input = "0.567"  # type: ignore
    assert backend.get_battery_sensor_current(0) == 0.567

    with pytest.raises(ValueError):
        backend.get_battery_sensor_current(1)


def test_backend_get_led_states() -> None:
    """Get the LED states."""
    backend = SRV4PowerBoardConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    assert not any([backend.get_led_state(i) for i in [0, 1]])  # noqa: C407

    with pytest.raises(KeyError):
        backend.get_led_state(7)


def test_backend_set_led_states() -> None:
    """Set the LED states."""
    backend = SRV4PowerBoardConsoleBackend(
        "TestBoard",
        console_class=MockConsole,
    )

    for i in [0, 1]:
        backend._console.expects = f"Set LED {i} to True"  # type: ignore
        backend.set_led_state(i, True)

    with pytest.raises(ValueError):
        backend.set_led_state(8, True)
