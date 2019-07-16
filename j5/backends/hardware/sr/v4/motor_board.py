"""Hardware Backend for the SR v4 motor board."""
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Callable,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    cast,
)

from serial import Serial, SerialException, SerialTimeoutException
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo

from j5.backends import Backend, CommunicationError
from j5.backends.hardware.env import HardwareEnvironment
from j5.boards import Board
from j5.boards.sr.v4.motor_board import MotorBoard
from j5.components.motor import MotorInterface, MotorSpecialState, MotorState

if TYPE_CHECKING:
    from typing_extensions import Protocol
else:
    class Protocol:
        """Dummy class since typing_extensions is not available at runtime."""

        pass

CMD_RESET = 0
CMD_VERSION = 1
CMD_MOTOR = [2, 3]
CMD_BOOTLOADER = 4

SPEED_COAST = 1
SPEED_BRAKE = 2

RT = TypeVar("RT")  # pragma: nocover


def handle_serial_error(func: Callable[..., RT]) -> Callable[..., RT]:  # type: ignore
    """
    Wrap functions that use the serial port, and rethrow the errors.

    This is a decorator that should be used to wrap any functions that call the serial
    interface. It will catch and rethrow the errors as a CommunicationError, so that it
    is more explicit what is going wrong.
    """
    @wraps(func)
    def catch_exceptions(*args, **kwargs):  # type: ignore
        try:
            return func(*args, **kwargs)
        except SerialTimeoutException as e:
            raise CommunicationError(f"Serial Timeout Error: {e}")
        except SerialException as e:
            raise CommunicationError(f"Serial Error: {e}")
    return catch_exceptions


def is_motor_board(port: ListPortInfo) -> bool:
    """Check if a ListPortInfo represents a MCV4B."""
    return port.manufacturer == "Student Robotics" and port.product == "MCV4B" \
        and port.vid == 0x0403 and port.pid == 0x6001


class Seriallike(Protocol):
    """
    Something that walks like a Serial and quacks like a Serial.

    This is used instead of hardcoding the Serial class to allow it to be mocked out.
    """

    def __init__(self,
                 port: Optional[str] = None,
                 baudrate: int = 9600,
                 bytesize: int = 8,
                 parity: str = 'N',
                 stopbits: float = 1,
                 timeout: Optional[float] = None):
        ...

    def close(self) -> None:
        """Close the connection."""
        ...

    def flush(self) -> None:
        """Flush all pending write operations."""
        ...

    def readline(self) -> bytes:
        """Read a line from the serial port."""
        ...

    def write(self, data: bytes) -> int:
        """Write data to the serial port."""
        ...


class SRV4MotorBoardHardwareBackend(
    MotorInterface,
    Backend,
):
    """The hardware implementation of the SR v4 motor board."""

    environment = HardwareEnvironment
    board = MotorBoard

    @classmethod
    def discover(
            cls,
            find: Callable = comports,
            serial_class: Type[Seriallike] = Serial,
    ) -> Set[Board]:
        """Discover all connected motor boards."""
        # Find all serial ports.
        ports: List[ListPortInfo] = find()

        # Get a list of boards from the ports.
        boards: Set[Board] = set()
        for port in filter(is_motor_board, ports):
            boards.add(
                MotorBoard(
                    port.serial_number,
                    SRV4MotorBoardHardwareBackend(port.device, serial_class),
                ),
            )

        return boards

    @handle_serial_error
    def __init__(self, serial_port: str, serial_class: Type[Seriallike] = Serial) -> None:
        # Initialise our stored values for the state.
        self._state: List[MotorState] = [
            MotorSpecialState.BRAKE
            for _ in range(0, 2)
        ]

        self._serial = serial_class(
            port=serial_port,
            baudrate=1000000,
            timeout=0.25,
        )

        # Check we have the correct firmware version.
        version = self.firmware_version
        if version != "3":
            raise CommunicationError(
                f"Unexpected firmware version: {version}, expected: \"3\".",
            )

        # Brake both of the motors
        for i, val in enumerate(self._state):
            self.set_motor_state(i, val)

    def __del__(self) -> None:
        """Clean up device on destruction of object."""
        # Brake both of the motors for safety
        for i, val in enumerate(self._state):
            self.set_motor_state(i, MotorSpecialState.BRAKE)

        self._serial.flush()
        self._serial.close()

    @handle_serial_error
    def send_command(self, command: int, data: Optional[int] = None) -> None:
        """Send a serial command to the board."""
        message: List[int] = [command]
        if data is not None:
            message += [data]
        bytes_written = self._serial.write(bytes(message))
        if len(message) != bytes_written:
            raise CommunicationError(
                "Mismatch in command bytes written to serial interface.",
            )

    @handle_serial_error
    def read_serial_line(self) -> str:
        """Read a line from the serial interface."""
        bdata = self._serial.readline()

        if len(bdata) == 0:
            raise CommunicationError(
                "Unable to communicate with motor board. ",
                "Is it correctly powered?",
            )

        ldata = bdata.decode('utf-8')
        return ldata.rstrip()

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        self.send_command(CMD_VERSION)
        firmware_data = self.read_serial_line()
        model = firmware_data[:5]
        if model != "MCV4B":
            raise CommunicationError(
                f"Unexpected model string: {model}, expected MCV4B.",
            )
        return firmware_data[6:]  # Strip model and return version

    def get_motor_state(self, identifier: int) -> MotorState:
        """Get the state of a motor."""
        # We are unable to read the state from the motor board,
        # so we'll get the last set value.
        return self._state[identifier]

    def set_motor_state(self, identifier: int, power: MotorState) -> None:
        """Set the state of a motor."""
        if identifier not in range(0, 2):
            raise ValueError(
                f"Invalid motor identifier: {identifier}, valid values are: 0, 1",
            )

        if power == MotorSpecialState.BRAKE:
            value = SPEED_BRAKE
        elif power == MotorSpecialState.COAST:
            value = SPEED_COAST
        else:
            ipower = cast(float, power)
            if not -1 <= ipower <= 1:
                raise ValueError(
                    "Only motor powers between -1 and 1 are supported.",
                )

            # We are using a range of -125 to 125 power so that it is equal in both
            # forward and reverse directions. This is due to BRAKE and COAST being
            # magic numbers.
            value = round(ipower * 125) + 128

        self._state[identifier] = power
        self.send_command(CMD_MOTOR[identifier], value)
