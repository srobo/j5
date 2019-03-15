"""Test the SR v4 PowerBoard backend and associated classes."""

import struct
from datetime import timedelta
from typing import List, Optional, Union

import pytest
import usb

from j5.backends.hardware.sr.v4.power_board import (
    CMD_READ_5VRAIL,
    CMD_READ_BATTERY,
    CMD_READ_BUTTON,
    CMD_READ_FWVER,
    CMD_READ_OUTPUT,
    CMD_WRITE_ERRORLED,
    CMD_WRITE_OUTPUT,
    CMD_WRITE_PIEZO,
    CMD_WRITE_RUNLED,
    ReadCommand,
    SRV4PowerBoardHardwareBackend,
    USBCommunicationError,
    WriteCommand,
    handle_usb_error,
)
from j5.boards.sr.v4.power_board import PowerBoard, PowerOutputPosition
from j5.components.piezo import Note


def test_read_command():
    """Test that ReadCommand behaves as expected."""
    rc = ReadCommand(1, 2)

    assert type(rc) is ReadCommand
    assert type(rc.code) is int
    assert type(rc.data_len) is int
    assert rc.code == 1
    assert rc.data_len == 2


def test_write_command():
    """Test that WriteCommand behaves as expected."""
    wc = WriteCommand(1)

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
    """Test that the CMD_READ_5VRAIL."""
    assert type(CMD_READ_5VRAIL) is ReadCommand
    assert CMD_READ_5VRAIL.code == 6
    assert CMD_READ_5VRAIL.data_len == 4


def test_cmd_read_battery():
    """Test that the CMD_READ_BATTERY."""
    assert type(CMD_READ_BATTERY) is ReadCommand
    assert CMD_READ_BATTERY.code == 7
    assert CMD_READ_BATTERY.data_len == 8


def test_cmd_read_button():
    """Test that the CMD_READ_BUTTON."""
    assert type(CMD_READ_BUTTON) is ReadCommand
    assert CMD_READ_BUTTON.code == 8
    assert CMD_READ_BUTTON.data_len == 4


def test_cmd_read_fwver():
    """Test that the CMD_READ_FWVER."""
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
    """Test that the CMD_WRITE_RUNLED."""
    assert type(CMD_WRITE_RUNLED) is WriteCommand
    assert CMD_WRITE_RUNLED.code == 6


def test_cmd_write_errorled():
    """Test that the CMD_WRITE_ERRORLED."""
    assert type(CMD_WRITE_ERRORLED) is WriteCommand
    assert CMD_WRITE_ERRORLED.code == 7


def test_cmd_write_piezo():
    """Test that the CMD_WRITE_PIEZO."""
    assert type(CMD_WRITE_PIEZO) is WriteCommand
    assert CMD_WRITE_PIEZO.code == 8


def test_usb_communication_error():
    """Test that USBCommunicationError works."""
    u = USBCommunicationError(usb.core.USBError("Test."))
    assert str(u) == "Test."
    assert issubclass(USBCommunicationError, Exception)


def test_usb_error_handler_decorator():
    """Test that the handle_usb_error decorator works."""
    @handle_usb_error
    def test_func():
        raise usb.core.USBError("Test")

    with pytest.raises(USBCommunicationError):
        test_func()


class MockUSBContext:
    """This class mocks the behaviour of usb.core.Context."""

    def dispose(self, device: "MockUSBPowerBoardDevice"):
        """Dispose of the device."""
        pass


class MockUSBPowerBoardDevice:
    """This class mocks the behaviour of a USB device for a Power Board."""

    def __init__(self, serial_number: str, fw_version: int = 3):
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
            return self.read_data(wValue, wIndex, data_or_wLength, timeout)
        if bmRequestType == 0x00:
            self.write_data(wValue, wIndex, data_or_wLength, timeout)
            return b""

        raise ValueError("Invalid Request Type for mock device.")

    def read_data(
        self,
        wValue: int = 0,
        wIndex: int = 0,
        data_or_wLength: Optional[Union[int, bytes]] = None,
        timeout: Optional[int] = None,
    ) -> bytes:
        """Mock reading data from a device."""
        assert wValue == 0  # Always 0 on read.

        if 0 <= wIndex < 6:
            return self.read_output(data_or_wLength)
        if wIndex == 7:
            return self.read_battery(data_or_wLength)
        if wIndex == 8:
            return self.read_button(data_or_wLength)
        if wIndex == 9:
            return self.read_fw(data_or_wLength)

        raise NotImplementedError

    def read_output(self, data_or_wLength: Union[int, bytes]):
        """Mock reading the output current."""
        assert int(data_or_wLength) == 4
        return struct.pack("<I", 1200)

    def read_battery(self, data_or_wLength: Union[int, bytes]):
        """Mock reading the battery sensor."""
        assert int(data_or_wLength) == 8
        return struct.pack("<II", 567, 982)

    def read_button(self, data_or_wLength: Union[int, bytes]):
        """Mock reading the button state."""
        assert int(data_or_wLength) == 4
        return struct.pack("<I", 0)  # Not Pressed

    def read_fw(self, data_or_wLength: Union[int, bytes]):
        """Mock reading the firmware number."""
        assert int(data_or_wLength) == 4
        return struct.pack("<I", self.firmware_version)

    def write_data(
        self,
        wValue: int = 0,
        wIndex: int = 0,
        data_or_wLength: Optional[Union[int, bytes]] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """Mock writing data to a device."""
        if 0 <= wIndex < 6:
            # Write Output.
            return self.write_bool(wValue, data_or_wLength)
        if wIndex == 6:
            return self.write_bool(wValue, data_or_wLength)
        if wIndex == 7:
            return self.write_bool(wValue, data_or_wLength)
        if wIndex == 8:
            # Buzz the Piezo
            return self.write_buzz(wValue, data_or_wLength)

        raise NotImplementedError

    def write_bool(self, wValue: int, data_or_wLength: Union[int, bytes]):
        """Pretend to write a bool."""
        assert wValue == 1 or wValue == 0
        assert data_or_wLength == b""

    def write_buzz(self, wValue: int, data_or_wLength: Union[int, bytes]):
        """Pretend to buzz."""
        assert wValue == 0
        frequency, duration_ms = struct.unpack("<HH", data_or_wLength)
        assert frequency >= 0
        assert duration_ms >= 0


def mock_find(
    find_all=True, *, idVendor: int, idProduct: int,
) -> List[MockUSBPowerBoardDevice]:
    """This function mocks the behaviour of usb.core.find."""
    assert idVendor == 0x1BDA
    assert idProduct == 0x0010
    assert find_all
    return [MockUSBPowerBoardDevice(f"SERIAL{n}") for n in range(0, 4)]


def test_backend_initialisation():
    """Test that we can initialise a Backend."""
    device = MockUSBPowerBoardDevice("SERIAL0")
    backend = SRV4PowerBoardHardwareBackend(device)
    assert type(backend) is SRV4PowerBoardHardwareBackend
    assert backend._usb_device is device

    assert len(backend._output_states) == 6
    assert not any(backend._output_states.values())  # Check initially all false.

    assert len(backend._led_states) == 2
    assert not any(backend._led_states.values())  # Check initially all false.


def test_backend_discover():
    """Test that the backend can discover boards."""
    found_boards = SRV4PowerBoardHardwareBackend.discover(find=mock_find)

    assert len(found_boards) == 4
    assert type(found_boards[0]) is PowerBoard


def test_backend_cleanup():
    """Test that the backend cleans things up properly."""
    device = MockUSBPowerBoardDevice("SERIAL0")
    backend = SRV4PowerBoardHardwareBackend(device)

    del backend


def test_backend_firmware_version():
    """Test that we can get the firmware version."""
    device = MockUSBPowerBoardDevice("SERIAL0")
    backend = SRV4PowerBoardHardwareBackend(device)

    assert backend.firmware_version == 3


def test_backend_bad_firmware_version():
    """Test that we can get the firmware version."""
    device = MockUSBPowerBoardDevice("SERIAL0", fw_version=2)
    with pytest.raises(NotImplementedError):
        SRV4PowerBoardHardwareBackend(device)


def test_backend_serial_number():
    """Test that we can get the serial number."""
    device = MockUSBPowerBoardDevice("SERIAL0")
    backend = SRV4PowerBoardHardwareBackend(device)

    assert backend.serial() == "SERIAL0"


def test_backend_get_power_output_enabled():
    """Test that we can read the enable status of a PowerOutput."""
    device = MockUSBPowerBoardDevice("SERIAL0")
    backend = SRV4PowerBoardHardwareBackend(device)

    for i in range(0, 6):
        assert not backend.get_power_output_enabled(i)

    with pytest.raises(ValueError):
        backend.get_power_output_enabled(6)


def test_backend_set_power_output_enabled():
    """Test that we can read the enable status of a PowerOutput."""
    device = MockUSBPowerBoardDevice("SERIAL0")
    backend = SRV4PowerBoardHardwareBackend(device)

    for i in range(0, 6):
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
