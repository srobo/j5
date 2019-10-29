"""Test the SR v4 motor board hardware backend and associated classes."""

from typing import List, Type, cast

import pytest
from serial import SerialException, SerialTimeoutException
from tests.backends.hardware.j5.mock_serial import MockSerial

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


class MotorSerial(MockSerial):
    """MotorSerial is the same as MockSerial, but includes data we expect to receive."""

    expected_baudrate = 1000000

    def respond_to_write(self, data: bytes) -> None:
        """Hook that can be overriden by subclasses to respond to sent data."""
        # We only end up returning data once, check for that here.
        if data == b'\x01':  # Version Command
            self.append_received_data(b'MCV4B:3', newline=True)

    def check_data_sent_by_constructor(self) -> None:
        """Check that the backend constructor sent expected data to the serial port."""
        self.check_sent_data(
            b'\x01'  # Version Check
            b'\x02\x02'  # Brake Motor 0 at init
            b'\x03\x02',  # Brake Motor 1 at init
        )


class MotorSerialBadWrite(MotorSerial):
    """MotorSerial, but never writes properly."""

    def write(self, data: bytes) -> int:
        """Don't write any data, always return 0."""
        return 0


class MotorSerialBadFirmware(MotorSerial):
    """MotorSerial but with the wrong firmware version."""

    def write(self, data: bytes) -> int:
        """Write data to the serial, but with the wrong fw version."""
        if data == b'\x01':  # Version Command
            self.append_received_data(b'MCV4B:5', newline=True)
        return len(data)


def test_backend_initialisation() -> None:
    """Test that we can initialise a backend."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)

    assert type(backend) is SRV4MotorBoardHardwareBackend
    assert type(backend._serial) is MotorSerial

    assert len(backend._state) == 2
    assert all(state == MotorSpecialState.BRAKE for state in backend._state)


def test_backend_bad_firmware_version() -> None:
    """Test that we can detect a bad firmware version."""
    with pytest.raises(CommunicationError):
        SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerialBadFirmware)


def test_backend_discover() -> None:
    """Test that the backend can discover boards."""
    found_boards = SRV4MotorBoardHardwareBackend.discover(mock_comports, MotorSerial)

    assert len(found_boards) == 2
    assert all(type(board) is MotorBoard for board in found_boards)

    assert all((int(board.serial[6:])) < 2 for board in found_boards)


def test_backend_send_command() -> None:
    """Test that the backend can send commands."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)
    serial = cast(MotorSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    backend.send_command(4)
    serial.check_sent_data(b"\x04")

    backend.send_command(2, 100)
    serial.check_sent_data(b'\x02d')


def test_backend_send_command_bad_write() -> None:
    """Test that an error is thrown if we can't write bytes."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)

    bad_serial_driver = MotorSerialBadWrite("COM0", baudrate=1000000, timeout=0.25)
    backend._serial = bad_serial_driver
    with pytest.raises(CommunicationError):
        backend.send_command(4)


def test_read_serial_line() -> None:
    """Test that we can we lines from the serial interface."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)
    serial = cast(MotorSerial, backend._serial)
    serial.check_data_sent_by_constructor()
    serial.append_received_data(b"Green Beans", newline=True)
    data = backend.read_serial_line()
    assert data == "Green Beans"


def test_read_serial_line_no_data() -> None:
    """Check that a communication error is thrown if we get no data."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)
    serial = cast(MotorSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    with pytest.raises(CommunicationError):
        backend.read_serial_line()


def test_get_firmware_version() -> None:
    """Test that we can get the firmware version from the serial interface."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)
    serial = cast(MotorSerial, backend._serial)
    serial.check_data_sent_by_constructor()
    assert backend.firmware_version == "3"
    serial.check_sent_data(b'\x01')

    serial.append_received_data(b'PBV4C:5', newline=True)
    with pytest.raises(CommunicationError):
        backend.firmware_version
    serial.check_sent_data(b'\x01')


def test_get_set_motor_state() -> None:
    """Test that we can get and set the motor state."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)
    serial = cast(MotorSerial, backend._serial)
    serial.check_data_sent_by_constructor()

    assert backend.get_motor_state(0) == MotorSpecialState.BRAKE
    assert backend.get_motor_state(1) == MotorSpecialState.BRAKE

    backend.set_motor_state(0, 0.65)
    serial.check_sent_data(b'\x02\xd1')
    assert backend.get_motor_state(0) == 0.65

    backend.set_motor_state(0, 1.0)
    serial.check_sent_data(b'\x02\xfd')
    assert backend.get_motor_state(0) == 1.0

    backend.set_motor_state(0, -1.0)
    serial.check_sent_data(b'\x02\x03')
    assert backend.get_motor_state(0) == -1.0

    backend.set_motor_state(0, MotorSpecialState.BRAKE)
    serial.check_sent_data(b'\x02\x02')
    assert backend.get_motor_state(0) == MotorSpecialState.BRAKE

    backend.set_motor_state(0, MotorSpecialState.COAST)
    serial.check_sent_data(b'\x02\x01')
    assert backend.get_motor_state(0) == MotorSpecialState.COAST

    with pytest.raises(ValueError):
        backend.set_motor_state(0, 20.0)
    serial.check_sent_data(b'')

    with pytest.raises(ValueError):
        backend.set_motor_state(2, 0.0)
    serial.check_sent_data(b'')


def test_brake_motors_at_deletion() -> None:
    """Test that both motors are set to BRAKE when the backend is garbage collected."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)
    serial = cast(MotorSerial, backend._serial)
    serial.check_data_sent_by_constructor()
    del backend
    serial.check_sent_data(
        b'\x02\x02'  # Brake motor 0
        b'\x03\x02',  # Brake motor 1
    )


def test_safe_shutdown_serial_start_crash() -> None:
    """Test that the _shutdown on the board doesn't break during start."""
    backend = SRV4MotorBoardHardwareBackend("COM0", serial_class=MotorSerial)

    # This line simulates the backend never initialising the state
    del backend._state

    # Check it worked.
    assert not hasattr(backend, "_state")

    # Now force a deconstruction event.
    del backend
