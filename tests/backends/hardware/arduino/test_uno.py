"""Tests for the Arduino Uno hardware implementation."""

from tests.backends.hardware.j5.mock_serial import MockSerial

from j5.backends.hardware.arduino.uno import ArduinoUnoHardwareBackend


class UnoSerial(MockSerial):
    """UnoSerial is the same as MockSerial, but includes data we expect to receive."""

    expected_baudrate = 115200


def test_backend_initialisation() -> None:
    """Test that we can initialise a ArduinoUnoHardwareBackend."""
    backend = ArduinoUnoHardwareBackend("/dev/ttyUSB1", UnoSerial)
    assert type(backend) is ArduinoUnoHardwareBackend
    assert type(backend._serial) is UnoSerial
