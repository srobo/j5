"""Tests for the Arduino Uno hardware implementation."""

from typing import Optional

import pytest
from tests.backends.hardware.j5.mock_serial import MockSerial

from j5.backends import CommunicationError
from j5.backends.hardware.arduino.uno import ArduinoUnoHardwareBackend
from j5.components import GPIOPinMode


class UnoSerial(MockSerial):
    """UnoSerial is the same as MockSerial, but includes data we expect to receive."""

    expected_baudrate = 115200
    firmware_version = "2019.6.0"

    def __init__(self,
                 port: Optional[str] = None,
                 baudrate: int = 9600,
                 bytesize: int = 8,
                 parity: str = 'N',
                 stopbits: float = 1,
                 timeout: Optional[float] = None,
                 ):
        super().__init__(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout,
        )
        self.append_received_data(b"# Booted", newline=True)
        version_line = b"# SBDuino GPIO v" + self.firmware_version.encode("utf-8")
        self.append_received_data(version_line, newline=True)


class UnoSerialOldVersion1(UnoSerial):
    """Like UnoSerial, but reports an older version number."""

    firmware_version = "2018.7.0"


class UnoSerialOldVersion2(UnoSerial):
    """Like UnoSerial, but reports an older version number."""

    firmware_version = "2019.5.0"


class UnoSerialNewVersion1(UnoSerial):
    """Like UnoSerial, but reports an newer version number."""

    firmware_version = "2019.6.1"


class UnoSerialNewVersion2(UnoSerial):
    """Like UnoSerial, but reports an newer version number."""

    firmware_version = "2019.7.0"


class UnoSerialNewVersion3(UnoSerial):
    """Like UnoSerial, but reports an newer version number."""

    firmware_version = "2020.1.0"


def test_backend_initialisation() -> None:
    """Test that we can initialise a ArduinoUnoHardwareBackend."""
    backend = ArduinoUnoHardwareBackend("COM0", UnoSerial)
    assert type(backend) is ArduinoUnoHardwareBackend
    assert type(backend._serial) is UnoSerial
    assert all(mode is GPIOPinMode.DIGITAL_INPUT for mode in backend._pins.values())


def test_backend_version_check() -> None:
    """Test that an exception is raised if the arduino reports an unsupported version."""
    with pytest.raises(CommunicationError):
        ArduinoUnoHardwareBackend("COM0", UnoSerialOldVersion1)
    with pytest.raises(CommunicationError):
        ArduinoUnoHardwareBackend("COM0", UnoSerialOldVersion2)
    ArduinoUnoHardwareBackend("COM0", UnoSerialNewVersion1)
    ArduinoUnoHardwareBackend("COM0", UnoSerialNewVersion2)
    ArduinoUnoHardwareBackend("COM0", UnoSerialNewVersion3)
