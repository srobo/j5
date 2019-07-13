"""Tests for the Arduino Uno hardware implementation."""

from tests.backends.hardware.j5.mock_serial import MockSerial

from j5.backends.hardware.arduino.uno import ArduinoUnoHardwareBackend
from j5.components import GPIOPinMode


class UnoSerial(MockSerial):
    """UnoSerial is the same as MockSerial, but includes data we expect to receive."""

    expected_baudrate = 115200
    initial_received_data = (
        b"# Booted\n"
        b"# SBDuino GPIO v2019.6.0\n"
    )


def test_backend_initialisation() -> None:
    """Test that we can initialise a ArduinoUnoHardwareBackend."""
    backend = ArduinoUnoHardwareBackend("COM0", UnoSerial)
    assert type(backend) is ArduinoUnoHardwareBackend
    assert type(backend._serial) is UnoSerial
    assert all(mode is GPIOPinMode.DIGITAL_INPUT for mode in backend._pins.values())
