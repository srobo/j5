"""Test the SR v4 Servo Board backend and associated classes."""

import struct
from typing import List, Optional, Union

import pytest

from j5.backends.hardware.j5.raw_usb import ReadCommand, WriteCommand
from j5.backends.hardware.sr.v4.servo_board import (
    CMD_READ_FWVER,
    CMD_WRITE_INIT,
    CMD_WRITE_SET_SERVO,
    SRV4ServoBoardHardwareBackend,
)
from j5.boards.sr.v4 import ServoBoard


def test_cmd_read_fwver() -> None:
    """Test that the CMD_READ_FWVER is as expected."""
    assert type(CMD_READ_FWVER) is ReadCommand
    assert CMD_READ_FWVER.code == 9
    assert CMD_READ_FWVER.data_len == 4


def test_cmd_write_init() -> None:
    """Test that the CMD_WRITE_INIT is as expected."""
    assert type(CMD_WRITE_INIT) is WriteCommand
    assert CMD_WRITE_INIT.code == 12


def test_cmd_write_servo() -> None:
    """Test the CMD_WRITE_SERVO command are as expected."""
    for i in range(0, 12):
        assert CMD_WRITE_SET_SERVO[i].code == i


class MockUSBContext:
    """This class mocks the behaviour of usb.core.Context."""

    def dispose(self, device: "MockUSBServoBoardDevice") -> None:
        """Dispose of the device."""
        pass


class MockUSBServoBoardDevice:
    """This class mocks the behaviour of a USB device for a Servo Board."""

    def __init__(self, serial_number: str, fw_version: int = 2):
        self.serial = serial_number
        self.firmware_version = fw_version
        self._ctx = MockUSBContext()  # Used by PyUSB when cleaning up the device.

    def serial_number(self) -> str:
        """Get the serial number of the USB device."""
        return self.serial

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
        assert bRequest == 64  # This is the same for read and write.

        if bmRequestType == 0x80:
            assert isinstance(data_or_wLength, int)
            return self.read_data(wValue, wIndex, data_or_wLength, timeout)
        if bmRequestType == 0x00:
            assert isinstance(data_or_wLength, bytes)
            self.write_data(wValue, wIndex, data_or_wLength, timeout)
            return b""

        raise ValueError("Invalid Request Type for mock device.")

    def read_data(
        self,
        wValue: int = 0,
        wIndex: int = 0,
        wLength: int = 0,
        timeout: Optional[int] = None,
    ) -> bytes:
        """Mock reading data from a device."""
        assert wValue == 0  # Always 0 on read.

        if wIndex == 9:
            return self.read_fw(wLength)

        raise NotImplementedError

    def read_fw(self, wLength: int) -> bytes:
        """Mock reading the firmware number."""
        assert wLength == 4
        return struct.pack("<I", self.firmware_version)

    def write_data(
        self,
        wValue: int = 0,
        wIndex: int = 0,
        data: bytes = b"",
        timeout: Optional[int] = None,
    ) -> None:
        """Mock writing data to a device."""
        if 0 <= wIndex < 12:
            # Set Servo.
            return self.write_servo(wValue, data)
        if wIndex == 12:
            # Initialise. Behaviour unknown currently
            return

        raise NotImplementedError

    def write_servo(self, wValue: int, data: bytes) -> None:
        """Set the value of a servo."""
        assert -100 <= wValue <= 100
        assert data == b''


def mock_find(
    find_all: bool = True, *, idVendor: int, idProduct: int,
) -> List[MockUSBServoBoardDevice]:
    """This function mocks the behaviour of usb.core.find."""
    assert idVendor == 0x1BDA
    assert idProduct == 0x0011
    assert find_all
    return [MockUSBServoBoardDevice(f"SERIAL{n}") for n in range(0, 4)]


def test_backend_initialisation() -> None:
    """Test that we can initialise a backend."""
    device = MockUSBServoBoardDevice("SERIAL0")
    backend = SRV4ServoBoardHardwareBackend(device)

    assert isinstance(backend, SRV4ServoBoardHardwareBackend)
    assert backend._usb_device is device

    assert len(backend._positions) == 12
    assert all(pos == 0.0 for pos in backend._positions)


def test_backend_discover() -> None:
    """Test that the backend can discover boards."""
    found_boards = SRV4ServoBoardHardwareBackend.discover(find=mock_find)

    assert len(found_boards) == 4
    assert all(type(board) is ServoBoard for board in found_boards)


def test_backend_cleanup() -> None:
    """Test that the backend cleans things up properly."""
    device = MockUSBServoBoardDevice("SERIAL0")
    backend = SRV4ServoBoardHardwareBackend(device)

    del backend


def test_backend_firmware_version() -> None:
    """Test that we can get the firmware version."""
    device = MockUSBServoBoardDevice("SERIAL0")
    backend = SRV4ServoBoardHardwareBackend(device)

    assert backend.firmware_version == "2"


def test_backend_bad_firmware_version() -> None:
    """Test that we can get the firmware version."""
    device = MockUSBServoBoardDevice("SERIAL0", fw_version=1)
    with pytest.raises(NotImplementedError):
        SRV4ServoBoardHardwareBackend(device)


def test_backend_serial_number() -> None:
    """Test that we can get the serial number."""
    device = MockUSBServoBoardDevice("SERIAL0")
    backend = SRV4ServoBoardHardwareBackend(device)

    assert backend.serial == "SERIAL0"


def test_backend_get_servo_status() -> None:
    """Test that we can get the position of a servo."""
    device = MockUSBServoBoardDevice("SERIAL0")
    backend = SRV4ServoBoardHardwareBackend(device)

    assert all(backend.get_servo_position(i) == 0.0 for i in range(0, 12))
