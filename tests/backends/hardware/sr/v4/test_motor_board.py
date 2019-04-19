"""Test the SR v4 motor board hardware backend and associated classes."""

from functools import partial
from typing import List, Optional, Type

import pytest
from serial import SerialException, SerialTimeoutException

from j5.backends import CommunicationError
from j5.backends.hardware.sr.v4.motor_board import (
    CMD_BOOTLOADER,
    CMD_MOTOR,
    CMD_RESET,
    CMD_VERSION,
    SPEED_BRAKE,
    SPEED_COAST,
    SRV4MotorBoardHardwareBackend,
    handle_serial_error,
)
from j5.boards.sr.v4 import MotorBoard
from j5.components import MotorSpecialState


def test_cmd_constants() -> None:
    """Test that the command constants are what we expect."""
    assert CMD_RESET == 0
    assert CMD_VERSION == 1
    assert CMD_BOOTLOADER == 4

    assert len(CMD_MOTOR) == 2
    assert CMD_MOTOR[0] == 2
    assert CMD_MOTOR[1] == 3


def test_speed_constants() -> None:
    """Test that the speed constants are what we expect."""
    assert SPEED_COAST == 1
    assert SPEED_BRAKE == 2


def test_serial_error_handler_decorator() -> None:
    """Test that the handle_serial_error decorator works."""
    @handle_serial_error
    def test_func(exception: Type[IOError]) -> None:
        raise exception()

    with pytest.raises(CommunicationError):
        test_func(SerialException)

    with pytest.raises(CommunicationError):
        test_func(SerialTimeoutException)


class MockSerial:
    """This class mocks the behaviour of serial.Serial."""

    def __init__(self,
                 port: Optional[str] = None,
                 baudrate: int = 9600,
                 bytesize: int = 8,
                 parity: str = 'N',
                 stopbits: float = 1,
                 timeout: Optional[float] = None,
                 expects: bytes = b'',
                 ):
        self._is_open: bool = True
        self._buffer: bytes = b''
        self.port = port
        self._expects = expects

        assert baudrate == 1000000
        assert bytesize == 8
        assert parity == 'N'
        assert stopbits == 1
        assert timeout is not None
        assert 0.1 <= timeout <= 0.3  # Acceptable range of timeouts

    def close(self) -> None:
        """Close the serial port."""
        assert self._is_open  # Check the port is open first.
        self._is_open = False

    def flush(self) -> None:
        """Flush the buffer on the serial port."""
        self._buffer = b''

    def read(self, size: int = 1) -> bytes:
        """Read size bytes from the input buffer."""
        assert len(self._buffer) >= size

        data = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return data

    def readline(self) -> bytes:
        """Read up to a newline on the serial port."""
        try:
            pos = self._buffer.index(b'\n')
        except ValueError:
            return b''
        return self.read(pos)

    def write(self, data: bytes) -> int:
        """Write the data to the serial port."""
        self.check_expects(data)

        # We only end up returning data once, check for that here.
        if data == b'\x01':  # Version Command
            self.buffer_append(b'MCV4B:3', newline=True)

        return len(data)

    # Functions for helping us mock.

    def buffer_append(self, data: bytes, newline: bool = False) -> None:
        """Append some data to the receive buffer."""
        self._buffer += data
        if newline:
            self._buffer += b'\n'

    def expects_prepend(self, data: bytes) -> None:
        """Prepend some bytes to the output buffer that we expect to see."""
        self._expects = data + self._expects

    def check_expects(self, data: bytes) -> None:
        """Check that the given data is what we expect to see on the output buffer."""
        length = len(data)
        assert data == self._expects[:length]
        self._expects = self._expects[length:]


class MockSerialBadWrite(MockSerial):
    """MockSerial, but never writes properly."""

    def write(self, data: bytes) -> int:
        """Don't write any data, always return 0."""
        return 0


class MockSerialBadFirmware(MockSerial):
    """MockSerial but with the wrong firmware version."""

    def write(self, data: bytes) -> int:
        """Write data to the serial, but with the wrong fw version."""
        if data == b'\x01':  # Version Command
            self.buffer_append(b'MCV4B:5', newline=True)
        return len(data)


class MockListPortInfo:
    """This class mocks the behaviour of serial.tools.ListPortInfo."""

    def __init__(
            self,
            device: str,
            serial_number: str,
            vid: int = 0x403,
            pid: int = 0x6001,
            manufacturer: str = "Student Robotics",
            product: str = "MCV4B",
    ) -> None:
        self.device = device
        self.serial_number = serial_number
        self.vid = vid
        self.pid = pid
        self.manufacturer = manufacturer
        self.product = product


def mock_comports(include_links: bool = False) -> List[MockListPortInfo]:
    """This function mocks the behaviour of serial.tools.list_ports_common.comports."""
    assert not include_links  # This should always be false. See PySerial docs.

    return [
        MockListPortInfo("COM0", "SERIAL0"),  # Valid Motor Board
        MockListPortInfo("COM1", "SERIAL1"),  # Valid Motor Board
        MockListPortInfo("COM2", "SERIAL2", vid=0x302),  # Bad VID
        MockListPortInfo("COM3", "SERIAL3", pid=0x3002),  # Bad PID
        MockListPortInfo("COM4", "SERIAL4", manufacturer="Acme Inc"),  # Bad Manufacturer
        MockListPortInfo("COM5", "SERIAL5", product="Not a Motor Board"),  # Bad Product
    ]


# MotorSerial is the same as MockSerial, but includes some data we expect to receive.
MotorSerial = partial(
    MockSerial,
    expects=b'\x01'  # Version Check
            b'\x02\x02'  # Brake Motor 0 at init
            b'\x03\x02'  # Brake Motor 1 at init
            b'\x02\x02'  # Brake Motor 0 at del
            b'\x03\x02',  # Brake Motor 1 at del
)


def test_backend_initialisation() -> None:
    """Test that we can initialise a backend."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)

    assert type(backend) is SRV4MotorBoardHardwareBackend
    assert type(backend._serial) is MockSerial

    assert len(backend._state) == 2
    assert all(state == MotorSpecialState.BRAKE for state in backend._state)


def test_backend_bad_firmware_version() -> None:
    """Test that we can detect a bad firmware version."""
    with pytest.raises(CommunicationError):
        SRV4MotorBoardHardwareBackend("COM0", serial_class=MockSerialBadFirmware)


def test_backend_discover() -> None:
    """Test that the backend can discover boards."""
    found_boards = SRV4MotorBoardHardwareBackend.discover(mock_comports, MotorSerial)

    assert len(found_boards) == 2
    assert all(type(board) is MotorBoard for board in found_boards)

    assert all((int(board.serial[6:])) < 2 for board in found_boards)


def test_backend_send_command() -> None:
    """Test that the backend can send commands."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)

    backend._serial.expects_prepend(b'\x04')
    backend.send_command(4)

    backend._serial.expects_prepend(b'\x02d')
    backend.send_command(2, 100)


def test_backend_send_command_bad_write() -> None:
    """Test that an error is thrown if we can't write bytes."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)

    bad_serial_driver = MockSerialBadWrite("COM0", baudrate=1000000, timeout=0.25)
    backend._serial = bad_serial_driver
    with pytest.raises(CommunicationError):
        backend.send_command(4)


def test_read_serial_line() -> None:
    """Test that we can we lines from the serial interface."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)
    backend._serial.flush()
    backend._serial.buffer_append(b"Green Beans", newline=True)
    data = backend.read_serial_line()
    assert data == "Green Beans"


def test_read_serial_line_no_data() -> None:
    """Check that a communication error is thrown if we get no data."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)
    backend._serial.flush()

    with pytest.raises(CommunicationError):
        backend.read_serial_line()


def test_get_firmware_version() -> None:
    """Test that we can get the firmware version from the serial interface."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)
    backend._serial.flush()
    backend._serial.expects_prepend(b'\x01')
    assert backend.firmware_version == "3"

    backend._serial.flush()
    backend._serial.expects_prepend(b'\x01')
    backend._serial.buffer_append(b'PBV4C:5', newline=True)
    with pytest.raises(CommunicationError):
        backend.firmware_version


def test_get_set_motor_state() -> None:
    """Test that we can get and set the motor state."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)

    assert backend.get_motor_state(0) == MotorSpecialState.BRAKE
    assert backend.get_motor_state(1) == MotorSpecialState.BRAKE

    backend._serial.expects_prepend(b'\x02\xd1')
    backend.set_motor_state(0, 0.65)
    assert backend.get_motor_state(0) == 0.65

    backend._serial.expects_prepend(b'\x02\xfd')
    backend.set_motor_state(0, 1.0)
    assert backend.get_motor_state(0) == 1.0

    backend._serial.expects_prepend(b'\x02\x03')
    backend.set_motor_state(0, -1.0)
    assert backend.get_motor_state(0) == -1.0

    backend._serial.expects_prepend(b'\x02\x02')
    backend.set_motor_state(0, MotorSpecialState.BRAKE)
    assert backend.get_motor_state(0) == MotorSpecialState.BRAKE

    backend._serial.expects_prepend(b'\x02\x01')
    backend.set_motor_state(0, MotorSpecialState.COAST)
    assert backend.get_motor_state(0) == MotorSpecialState.COAST

    with pytest.raises(ValueError):
        backend.set_motor_state(0, 20.0)

    with pytest.raises(ValueError):
        backend.set_motor_state(2, 0.0)
