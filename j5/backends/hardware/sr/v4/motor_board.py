"""Hardware Backend for the SR v4 motor board."""
from typing import List, Optional

from serial.tools.list_ports import comports

from j5.backends import Backend
from j5.backends.hardware.env import HardwareEnvironment
from j5.boards import Board
from j5.boards.sr.v4.motor_board import MotorBoard
from j5.components import MotorInterface
from j5.components.motor import MotorState


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

    def __init__(self, serial_port: str):
        pass

    def get_firmware_version(self) -> Optional[str]:
        """Get the firmware version of the board."""
        pass

    def get_motor_state(self, identifier: int) -> MotorState:
        """Get the state of a motor."""
        pass

    def set_motor_state(self, identifier: int, power: MotorState) -> None:
        """Set the state of a motor."""
        pass
