"""Hardware Backend for the SR v4 motor board."""
from threading import Lock
from typing import List, Optional, Set, cast

from serial import SerialException, SerialTimeoutException
from serial.tools.list_ports_common import ListPortInfo

from j5.backends import Backend, CommunicationError
from j5.backends.hardware import DeviceMissingSerialNumberError
from j5.backends.hardware.j5.serial import SerialHardwareBackend
from j5.boards import Board
from j5.boards.sr.v4.motor_board import MotorBoard
from j5.components.motor import MotorInterface, MotorSpecialState, MotorState

CMD_RESET = 0
CMD_VERSION = 1
CMD_MOTOR = [2, 3]
CMD_BOOTLOADER = 4

SPEED_COAST = 1
SPEED_BRAKE = 2


def is_motor_board(port: ListPortInfo) -> bool:
    """
    Check if a ListPortInfo represents a MCV4B.

    :param port: ListPortInfo object.
    :returns: True if object represents motor board.
    """
    return port.manufacturer == "Student Robotics" and port.product == "MCV4B" \
        and port.vid == 0x0403 and port.pid == 0x6001


class SRV4MotorBoardHardwareBackend(
    MotorInterface,
    SerialHardwareBackend,
):
    """The hardware implementation of the SR v4 motor board."""

    board = MotorBoard

    @classmethod
    def discover(cls) -> Set[Board]:
        """
        Discover boards that this backend can control.

        :returns: set of boards that this backend can control.
        :raises DeviceMissingSerialNumberError: a board without a serial number was found.
        """
        # Find all serial ports.
        ports = cls.get_comports()

        # Get a list of boards from the ports.
        boards: Set[Board] = set()
        for port in filter(is_motor_board, ports):
            if port.serial_number is None:
                raise DeviceMissingSerialNumberError(
                    "Found motor board-like device without serial number. "
                    f"The motor board is likely to be damaged: {port.usb_info()}",
                )
            else:
                boards.add(
                    MotorBoard(
                        port.serial_number,
                        cast(
                            Backend,
                            cls(port.device),
                        ),
                    ),
                )

        return boards

    def __init__(
        self,
        serial_port: str,
    ) -> None:
        super().__init__(
            serial_port=serial_port,
            baud=1000000,
        )

        # Initialise our stored values for the state.
        self._state: List[MotorState] = [
            MotorSpecialState.BRAKE
            for _ in range(0, 2)
        ]

        self._lock = Lock()

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
        """
        Clean up device on destruction of object.

        :raises CommunicationError: Error occurred during motor board comms.
        """
        # Brake both of the motors for safety
        if hasattr(self, "_state"):
            for i, _ in enumerate(self._state):
                self.set_motor_state(
                    i,
                    MotorSpecialState.BRAKE,
                    acquire_lock=False,
                )
        try:
            self._serial.flush()
            self._serial.close()
        except SerialTimeoutException as e:
            raise CommunicationError(f"Serial Timeout Error: {e}") from e
        except SerialException as e:
            raise CommunicationError(f"Serial Error: {e}") from e

    def send_command(self, command: int, data: Optional[int] = None) -> None:
        """
        Send a serial command to the board.

        :param command: Command ID to send.
        :param data: Data for command, if any.
        """
        with self._lock:
            self._send_command_no_lock(command, data)

    def _send_command_no_lock(self, command: int, data: Optional[int] = None) -> None:
        """
        Send a serial command to the board without acquiring the lock.

        :param command: Command ID to send.
        :param data: Data for command, if any.
        :raises CommunicationError: Error occurred during motor board comms.
        """
        try:
            message: List[int] = [command]
            if data is not None:
                message += [data]
            bytes_written = self._serial.write(bytes(message))
            if len(message) != bytes_written:
                raise CommunicationError(
                    "Mismatch in command bytes written to serial interface.",
                )
        except SerialTimeoutException as e:
            raise CommunicationError(f"Serial Timeout Error: {e}") from e
        except SerialException as e:
            raise CommunicationError(f"Serial Error: {e}") from e

    @property
    def firmware_version(self) -> Optional[str]:
        """
        The firmware version reported by the board.

        :returns: firmware version reported by the board, if any.
        :raises CommunicationError: Not a motor board!
        """
        with self._lock:
            self._send_command_no_lock(CMD_VERSION)
            firmware_data = self.read_serial_line()
        model = firmware_data[:5]
        if model != "MCV4B":
            raise CommunicationError(
                f"Unexpected model string: {model}, expected MCV4B.",
            )
        return firmware_data[6:]  # Strip model and return version

    def get_motor_state(self, identifier: int) -> MotorState:
        """
        Get the current motor state.

        :param identifier: identifier of the motor
        :returns: state of the motor.
        """
        # We are unable to read the state from the motor board,
        # so we'll get the last set value.
        return self._state[identifier]

    def set_motor_state(
            self,
            identifier: int,
            power: MotorState,
            acquire_lock: bool = True,
    ) -> None:
        """
        Set the state of a motor.

        :param identifier: identifier of the motor
        :param power: state of the motor.
        :param acquire_lock: whether to acquire lock. dangerous if false.
        :raises ValueError: invalid motor identifier.
        """
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

        command = CMD_MOTOR[identifier]

        if acquire_lock:
            self.send_command(command, value)
        else:
            self._send_command_no_lock(command, value)
