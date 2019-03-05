"""Test the SR v4 PowerBoard backend and associated classes."""

from typing import List, Optional, Union

from j5.boards.sr.v4.power_board import PowerOutputPosition, PowerBoard
from j5.backends.hardware.sr.v4.power_board import (
    ReadCommand,
    WriteCommand,
    CMD_READ_OUTPUT,
    CMD_READ_5VRAIL,
    CMD_READ_BATTERY,
    CMD_READ_BUTTON,
    CMD_READ_FWVER,
    CMD_WRITE_OUTPUT,
    CMD_WRITE_RUNLED,
    CMD_WRITE_ERRORLED,
    CMD_WRITE_PIEZO,
    SRV4PowerBoardHardwareBackend,
)


def test_read_command():
    """Test that ReadCommand behaves as expected."""
    rc = ReadCommand(1, 2)
    assert issubclass(ReadCommand, tuple)

    assert type(rc) is ReadCommand
    assert type(rc.code) is int
    assert type(rc.data_len) is int
    assert rc.code == 1
    assert rc.data_len == 2


def test_write_command():
    """Test that WriteCommand behaves as expected."""
    wc = WriteCommand(1)
    assert issubclass(WriteCommand, tuple)

    assert type(wc) is WriteCommand
    assert type(wc.code) is int
    assert wc.code == 1


def test_cmd_read_output():
    """Test that CMD_READ_OUTPUT works."""

    assert len(CMD_READ_OUTPUT) == 6

    for pos in PowerOutputPosition:
        assert pos.value in CMD_READ_OUTPUT
        command = CMD_READ_OUTPUT[pos.value]
        assert pos.value == command.code
        assert command.data_len == 4


def test_cmd_read_5vrail():
    """Test that the CMD_READ_5VRAIL"""
    assert type(CMD_READ_5VRAIL) is ReadCommand
    assert CMD_READ_5VRAIL.code == 6
    assert CMD_READ_5VRAIL.data_len == 4


def test_cmd_read_battery():
    """Test that the CMD_READ_BATTERY"""
    assert type(CMD_READ_BATTERY) is ReadCommand
    assert CMD_READ_BATTERY.code == 7
    assert CMD_READ_BATTERY.data_len == 8


def test_cmd_read_button():
    """Test that the CMD_READ_BUTTON"""
    assert type(CMD_READ_BUTTON) is ReadCommand
    assert CMD_READ_BUTTON.code == 8
    assert CMD_READ_BUTTON.data_len == 4


def test_cmd_read_fwver():
    """Test that the CMD_READ_FWVER"""
    assert type(CMD_READ_FWVER) is ReadCommand
    assert CMD_READ_FWVER.code == 9
    assert CMD_READ_FWVER.data_len == 4


def test_cmd_write_output():
    """Test that CMD_WRITE_OUTPUT works."""

    assert len(CMD_WRITE_OUTPUT) == 6

    for pos in PowerOutputPosition:
        assert pos.value in CMD_WRITE_OUTPUT
        command = CMD_WRITE_OUTPUT[pos.value]
        assert pos.value == command.code


def test_cmd_write_runled():
    """Test that the CMD_WRITE_RUNLED"""
    assert type(CMD_WRITE_RUNLED) is WriteCommand
    assert CMD_WRITE_RUNLED.code == 6


def test_cmd_write_errorled():
    """Test that the CMD_WRITE_ERRORLED"""
    assert type(CMD_WRITE_ERRORLED) is WriteCommand
    assert CMD_WRITE_ERRORLED.code == 7


def test_cmd_write_piezo():
    """Test that the CMD_WRITE_PIEZO"""
    assert type(CMD_WRITE_PIEZO) is WriteCommand
    assert CMD_WRITE_PIEZO.code == 8


class MockUSBContext:
    """This class mocks the behaviour of usb.core.Context."""

    def dispose(self, device: 'MockUSBDevice'):
        """Dispose of the device."""
        pass


class MockUSBDevice:
    """This class mocks the behaviour of usb.core.Device."""

    def __init__(self, serial_number: str):
        self.serial = serial_number
        self._ctx = MockUSBContext()

    def serial_number(self) -> str:
        """Get the serial number of the USB device."""
        return self.serial

    def ctrl_trnsfer(
            self,
            bmRequestType: int,
            bRequest: int,
            wValue: int = 0,
            wIndex: int = 0,
            data_or_wLength: Optional[Union[int, bytes]] = None,
            timeout: Optional[int] = None,
    ) -> bytes:
        return b""


def mock_find(find_all=True, *, idVendor: int, idProduct: int) -> List[MockUSBDevice]:
    """This function mocks the behaviour of usb.core.find."""
    assert idVendor == 0x1bda
    assert idProduct == 0x0010
    if find_all:
        return [
            MockUSBDevice(f"SERIAL{n}")
            for n in range(0, 4)
        ]
    else:
        return [MockUSBDevice("SERIAL0")]


def test_backend_initialisation():
    device = MockUSBDevice("SERIAL0")
    backend = SRV4PowerBoardHardwareBackend(device)
    assert type(backend) is SRV4PowerBoardHardwareBackend
    assert backend._usb_device is device

    assert len(backend._output_states) == 6
    assert not any(backend._output_states.values())  # Check initially all false.

    assert len(backend._led_states) == 2
    assert not any(backend._led_states.values())  # Check initially all false.


def test_backend_discover():

    found_boards = SRV4PowerBoardHardwareBackend.discover(find=mock_find)

    assert len(found_boards) == 4
    assert type(found_boards[0]) is PowerBoard


