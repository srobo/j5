"""Test the backend for the SR v4 Power Board serial protocol."""
from typing import List, Optional, Type, cast

import pytest
from serial import Serial
from serial.tools.list_ports_common import ListPortInfo

from j5.backends.hardware import DeviceMissingSerialNumberError
from j5.backends.hardware.sr.v4.serial import (
    SRV4SerialProtocolPowerBoardHardwareBackend,
)
from j5.boards.sr.v4 import PowerBoard
from tests.backends.hardware.j5.mock_serial import MockSerial


class MockListPortInfo:
    """This class mocks the behaviour of serial.tools.ListPortInfo."""

    def __init__(
            self,
            device: str,
            serial_number: Optional[str],
            vid: int = 0x1bda,
            pid: int = 0x0010,
            manufacturer: str = "Student Robotics",
            product: str = "PBV4B",
    ) -> None:
        self.device = device
        self.serial_number = serial_number
        self.vid = vid
        self.pid = pid
        self.manufacturer = manufacturer
        self.product = product

    def usb_info(self) -> str:
        """Get a string containing information about the device."""
        return "USB Information"


class MockPowerSerialBackend(SRV4SerialProtocolPowerBoardHardwareBackend):
    """Mock backend for testing."""

    @classmethod
    def get_comports(cls) -> List[ListPortInfo]:
        """Get the comports."""
        return [
            MockListPortInfo("COM0", "SERIAL0"),  # Valid Power Board
            MockListPortInfo("COM1", "SERIAL1"),  # Valid Power Board
            MockListPortInfo("COM2", "SERIAL2", vid=0x302),  # Bad VID
            MockListPortInfo("COM3", "SERIAL3", pid=0x3002),  # Bad PID
            MockListPortInfo("COM4", "SERIAL4", manufacturer="Acme Inc"),  # Bad Manufacturer
            MockListPortInfo("COM5", "SERIAL5", product="Not a Power Board"),  # Bad Product
        ]

    def get_serial_class(self) -> Type[Serial]:
        """Get the serial class."""
        return PowerSerial  # type: ignore


class MockPowerSerialBadSerialNumberBackend(SRV4SerialProtocolPowerBoardHardwareBackend):
    """Mock backend for testing."""

    @classmethod
    def get_comports(cls) -> List[ListPortInfo]:
        """Get the comports."""
        return [
            MockListPortInfo("COM0", None),  # type: ignore
        ]



class PowerSerial(MockSerial):
    """PowerSerial is the same as MockSerial, but includes data we expect to receive."""

    expected_baudrate = 115200

    def respond_to_write(self, data: bytes) -> None:
        """Hook that can be overriden by subclasses to respond to sent data."""
        if data == b'*IDN?\n':  # Identify Command
            self.append_received_data(b'Student Robotics:PBv4B:srABC:4.4', newline=True)
        elif data == b'*RESET\n':
            self.append_received_data(b'ACK', newline=True)
        elif data == b'OUT:0:I?\n':
            self.append_received_data(b'1.2', newline=True)
        else:
            self.append_received_data(b'NACK:Unrecognised command: ' + data, newline=True)

    def check_data_sent_by_constructor(self) -> None:
        """Check that the backend constructor sent expected data to the serial port."""
        self.check_sent_data(
            b'*IDN?\n'  # Version Check
            b'*RESET\n'  # Reset the board
        )


class TestSRV4SerialProtocolPowerBoardHardwareBackend:
    """Test the backend for the SR v4 Power Board serial protocol."""

    def test_backend_discover(self) -> None:
        """Test that we correctly discover the two valid boards."""
        found_boards = MockPowerSerialBackend.discover()
        assert len(found_boards) == 2
        assert all(type(board) is PowerBoard for board in found_boards)

        assert {board.serial_number for board in found_boards} == {"SERIAL0", "SERIAL1"}

    def test_backend_discover_missing_serial_number(self) -> None:
        """Test that we correctly handle power boards without a serial number."""
        with pytest.raises(DeviceMissingSerialNumberError) as e:
            MockPowerSerialBadSerialNumberBackend.discover()
        assert e.match(
            "Found power board-like device without serial number. "
            "The power board is likely to be damaged: USB Information",
        )

    def test_backend_resets_board(self) -> None:
        """Test that we reset the board when it is initialised."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()

        # TODO: Check Make Safe too

    def test_get_power_output_current(self) -> None:
        """Test that we can fetch the current of a given power output."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        assert backend.get_power_output_current(0) == 1.2
        serial.check_sent_data(b"OUT:0:I?\n")

    def test_get_power_output_current_bad_identifier(self) -> None:
        """Test that we correctly handle an out of range power output."""
        backend = MockPowerSerialBackend("COM0")
        serial = cast(PowerSerial, backend._serial)
        serial.check_data_sent_by_constructor()
        with pytest.raises(ValueError) as e:
            backend.get_power_output_current(8)
        serial.check_sent_data(b"")
        assert e.match(
            "Invalid identifier: 8"
        )
