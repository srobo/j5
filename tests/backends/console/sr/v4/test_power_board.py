"""Test the SR v4 PowerBoard backend and associated classes."""

# from datetime import timedelta
from typing import TypeVar

import pytest

from j5.backends.console import Console
from j5.backends.console.sr.v4.power_board import SRV4PowerBoardConsoleBackend

# from j5.components.piezo import Note


T = TypeVar("T")


def test_backend_initialisation():
    """Test that we can initialise a Backend."""
    backend = SRV4PowerBoardConsoleBackend("Test")
    assert type(backend) is SRV4PowerBoardConsoleBackend

    assert len(backend._output_states) == 6
    assert not any(backend._output_states.values())  # Check initially all false.

    assert len(backend._led_states) == 2
    assert not any(backend._led_states.values())  # Check initially all false.


def test_backend_discover():
    """
    Test that the backend can not discover boards.

    This backend does not support discovery.
    """
    with pytest.raises(NotImplementedError):
        SRV4PowerBoardConsoleBackend.discover()


def test_backend_firmware_version():
    """Test that we can get the firmware version."""
    backend = SRV4PowerBoardConsoleBackend("TestBoard")

    assert backend.firmware_version is None


def test_backend_serial_number():
    """Test that we can get the serial number."""
    backend = SRV4PowerBoardConsoleBackend("TestBoard")

    assert backend.serial == "TestBoard"


def test_backend_get_power_output_enabled():
    """Test that we can read the enable status of a PowerOutput."""
    backend = SRV4PowerBoardConsoleBackend("TestBoard")

    for i in range(0, 6):
        assert not backend.get_power_output_enabled(i)

    with pytest.raises(ValueError):
        backend.get_power_output_enabled(6)


def test_backend_set_power_output_enabled():
    """Test that we can read the enable status of a PowerOutput."""
    class SetPowerOutputTestConsole(Console):
        """Test Console for testing the power outputs."""

        def __init__(self, descriptor: str):
            super(Console, self).__init__()
            self.expects = ""

        def info(self, message: str) -> None:
            """Mock writing to the terminal."""
            assert message == self.expects

    backend = SRV4PowerBoardConsoleBackend(
        "TestBoard", console_class=SetPowerOutputTestConsole)

    for i in range(0, 6):
        backend._console.expects = ""
        backend.set_power_output_enabled(i, True)

    with pytest.raises(ValueError):
        backend.set_power_output_enabled(6, True)


def test_backend_get_power_output_current():
    """Test that we can read the current on a PowerOutput."""
    device = MockUSBPowerBoardDevice("SERIAL0")
    backend = SRV4PowerBoardHardwareBackend(device)

    for i in range(0, 6):
        assert 1.2 == backend.get_power_output_current(i)

    with pytest.raises(ValueError):
        backend.get_power_output_current(6)


def test_backend_piezo_buzz():
    """Test that we can buzz the Piezo."""
    device = MockUSBPowerBoardDevice("SERIAL0")
    backend = SRV4PowerBoardHardwareBackend(device)

    # Buzz a Note
    backend.buzz(0, timedelta(seconds=10), Note.D7)

    # Buzz a frequency
    backend.buzz(0, timedelta(seconds=10), 100)

    # Buzz for too long.
    with pytest.raises(ValueError):
        backend.buzz(0, timedelta(seconds=100), 10)

    # Test non-existent buzzer
    with pytest.raises(ValueError):
        backend.buzz(1, timedelta(seconds=10), 0)


def test_backend_get_button_state():
    """Test that we can get the button state."""
    device = MockUSBPowerBoardDevice("SERIAL0")
    backend = SRV4PowerBoardHardwareBackend(device)

    assert not backend.get_button_state(0)

    with pytest.raises(ValueError):
        backend.get_button_state(1)


def test_backend_get_battery_sensor_voltage():
    """Test that we can get the battery sensor voltage."""
    device = MockUSBPowerBoardDevice("SERIAL0")
    backend = SRV4PowerBoardHardwareBackend(device)

    assert backend.get_battery_sensor_voltage(0) == 0.982

    with pytest.raises(ValueError):
        backend.get_battery_sensor_voltage(1)


def test_backend_get_battery_sensor_current():
    """Test that we can get the battery sensor current."""
    device = MockUSBPowerBoardDevice("SERIAL0")
    backend = SRV4PowerBoardHardwareBackend(device)

    assert backend.get_battery_sensor_current(0) == 0.567

    with pytest.raises(ValueError):
        backend.get_battery_sensor_current(1)


def test_backend_get_led_states():
    """Get the LED states."""
    device = MockUSBPowerBoardDevice("SERIAL0")
    backend = SRV4PowerBoardHardwareBackend(device)

    assert not any([backend.get_led_state(i) for i in [0, 1]])  # noqa: C407

    with pytest.raises(KeyError):
        backend.get_led_state(7)


def test_backend_set_led_states():
    """Set the LED states."""
    device = MockUSBPowerBoardDevice("SERIAL0")
    backend = SRV4PowerBoardHardwareBackend(device)

    for i in [0, 1]:
        backend.set_led_state(i, True)

    with pytest.raises(ValueError):
        backend.set_led_state(8, True)
