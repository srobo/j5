"""Test the abstract Raw USB backend."""
from threading import Lock
from typing import Optional, Set, Type, Union

import usb
from pytest import raises

from j5.backends.hardware.j5.raw_usb import (
    RawUSBHardwareBackend,
    ReadCommand,
    USBCommunicationError,
    WriteCommand,
)
from j5.boards import Board
from j5.components import Component
from tests.backends.hardware.sr.v4.test_power_board import MockUSBContext


def test_read_command() -> None:
    """Test that ReadCommand behaves as expected."""
    rc = ReadCommand(1, 2)

    assert type(rc) is ReadCommand
    assert type(rc.code) is int
    assert type(rc.data_len) is int
    assert rc.code == 1
    assert rc.data_len == 2


def test_write_command() -> None:
    """Test that WriteCommand behaves as expected."""
    wc = WriteCommand(1)

    assert type(wc) is WriteCommand
    assert type(wc.code) is int
    assert wc.code == 1


def test_usb_communication_error() -> None:
    """Test that USBCommunicationError works."""
    u = USBCommunicationError(usb.core.USBError("Test."))
    assert str(u) == "Test."
    assert issubclass(USBCommunicationError, Exception)


class MockBoard(Board):
    """A mock board."""

    @property
    def name(self) -> str:
        """A human friendly name for this board."""
        return "Mock Board."

    @property
    def serial_number(self) -> str:
        """The serial number of the board."""
        return "N/A"

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return "0.0.0"

    @staticmethod
    def make_safe() -> None:
        """Make all components on this board safe."""

    @staticmethod
    def supported_components() -> Set[Type[Component]]:
        """The components supported by this board."""
        return set()


class MockRawUSBDevice(usb.core.Device):
    """This class mocks the behaviour of a broken USB device."""

    def __init__(self) -> None:
        pass

    @property
    def serial_number(self) -> str:
        """Get the serial number of the USB device."""
        raise usb.core.USBError("Oh no.")

    @property
    def _ctx(self) -> MockUSBContext:
        """Get the USB context."""
        return MockUSBContext()

    def ctrl_transfer(
        self,
        bmRequestType: int,
        bRequest: int,
        wValue: int = 0,
        wIndex: int = 0,
        data_or_wLength: Optional[Union[int, bytes]] = None,
        timeout: Optional[int] = None,
    ) -> bytes:
        """Mock a control transfer."""
        raise usb.core.USBError("Oh no.")

    def read_data(
        self,
        wValue: int = 0,
        wIndex: int = 0,
        wLength: int = 0,
        timeout: Optional[int] = None,
    ) -> bytes:
        """Mock reading data from a device."""
        raise usb.core.USBError("Oh no.")

    def write_data(
        self,
        wValue: int = 0,
        wIndex: int = 0,
        data: bytes = b"",
        timeout: Optional[int] = None,
    ) -> None:
        """Mock writing data to a device."""
        raise usb.core.USBError("Oh no.")


class MockRawUSBHardwareBackend(RawUSBHardwareBackend):
    """A mock backend."""

    board = MockBoard

    def __init__(self) -> None:
        self._lock = Lock()
        self._usb_device = MockRawUSBDevice()

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover no boards."""
        return set()

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version."""
        return "v0.0.0"


def test_serial_number_exception_handler() -> None:
    """Test for right exception thrown if a USBError occurs."""
    backend = MockRawUSBHardwareBackend()

    with raises(USBCommunicationError):
        _ = backend.serial


def test_read_exception_handler() -> None:
    """Test for right exception thrown if a USBError occurs."""
    backend = MockRawUSBHardwareBackend()

    with raises(USBCommunicationError):
        backend._read(ReadCommand(1, 0))


def test_write_exception_handler() -> None:
    """Test for right exception thrown if a USBError occurs."""
    backend = MockRawUSBHardwareBackend()

    with raises(USBCommunicationError):
        backend._write(WriteCommand(1), 1)
