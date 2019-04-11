"""Hardware Backend for the SR v4 motor board."""
from typing import List, Optional, cast

from serial import Serial
from serial.tools.list_ports import comports

from j5.backends import Backend, CommunicationError
from j5.backends.hardware.env import HardwareEnvironment
from j5.boards import Board
from j5.boards.sr.v4.motor_board import MotorBoard
from j5.components.motor import MotorInterface, MotorSpecialState, MotorState

CMD_RESET = 0
CMD_VERSION = 1
CMD_MOTOR = [2, 3]
CMD_BOOTLOADER = 4

SPEED_COAST = 1
SPEED_BRAKE = 2


class SRV4MotorBoardHardwareBackend(
    MotorInterface,
    Backend,
):
    """The hardware implementation of the SR v4 motor board."""

    environment = HardwareEnvironment
    board = MotorBoard

    @classmethod
    def discover(cls) -> List[Board]:
        """Discover all connected motor boards."""
        # Find all serial ports.
        ports = comports()

        # Filter down to just motor boards.
        ports = list(filter(lambda x: x.manufacturer == "Student Robotics", ports))
        ports = list(filter(lambda x: x.product == "MCV4B", ports))
        ports = list(filter(lambda x: x.vid == 0x403, ports))  # FTDI, Ltd
        ports = list(filter(lambda x: x.pid == 0x6001, ports))  # FT232 Serial (UART) IC

        # Get a list of boards from the ports.
        boards: List[Board] = []
        for port in ports:
            boards.append(
                MotorBoard(
                    port.serial_number,
                    SRV4MotorBoardHardwareBackend(port.device),
                ),
            )

        return boards

    def __init__(self, serial_port: str) -> None:
        self._serial = Serial(
            port=serial_port,
            baudrate=1000000,
            timeout=0.25,
        )

        # Check we have the correct firmware version.
        version = self.get_firmware_version()
        if version != "3":
            raise CommunicationError(
                f"Unexpected firmware version: {version}, expected: 3.",
            )

        # Initialise our stored values for the state.
        self._state: List[MotorState] = [
            MotorSpecialState.BRAKE
            for _ in range(0, 2)
        ]

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

    def send_command(self, command: int, data: Optional[int] = None) -> None:
        """Send a serial command to the board."""
        command_bytes = chr(command).encode('utf-8')
        bytes_written = self._serial.write(command_bytes)
        if len(command_bytes) != bytes_written:
            raise CommunicationError(
                "Mismatch in command bytes written to serial interface.",
            )

        if data is not None:
            data_bytes = chr(data).encode()
            bytes_written = self._serial.write(data_bytes)
            if len(data_bytes) != bytes_written:
                raise CommunicationError(
                    "Mismatch in data bytes written to serial interface.",
                )

    def read_serial_line(self) -> str:
        """Read a line from the serial interface."""
        bdata = self._serial.readline()
        ldata = bdata.decode('utf-8')
        return ldata.rstrip()

    def get_firmware_version(self) -> Optional[str]:
        """Get the firmware version of the board."""
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
