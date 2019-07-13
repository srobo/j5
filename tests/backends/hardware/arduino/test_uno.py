"""Tests for the Arduino Uno hardware implementation."""

from typing import Optional

from tests.backends.hardware.j5.mock_serial import MockSerial

from j5.backends.hardware.arduino.uno import ArduinoUnoHardwareBackend


class UnoSerial(MockSerial):
    """UnoSerial is the same as MockSerial, but includes data we expect to receive."""

    def __init__(self,
                 port: Optional[str] = None,
                 baudrate: int = 9600,
                 bytesize: int = 8,
                 parity: str = 'N',
                 stopbits: float = 1,
                 timeout: Optional[float] = None):
        super().__init__(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout,
            expects=b"",
            expected_baudrate=115200,
        )


def test_backend_initialisation() -> None:
    """Test that we can initialise a ArduinoUnoHardwareBackend."""
    backend = ArduinoUnoHardwareBackend("/dev/ttyUSB1", UnoSerial)
    assert type(backend) is ArduinoUnoHardwareBackend
    assert type(backend._serial) is UnoSerial
