"""Arduino Uno Hardware Implementation."""

from typing import Callable, List, Optional, Set, Tuple, Type

from serial import Serial
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo

from j5.backends import CommunicationError
from j5.backends.hardware.env import HardwareEnvironment
from j5.backends.hardware.j5.serial import (
    SerialHardwareBackend,
    handle_serial_error,
)
from j5.boards import Board
from j5.boards.arduino.uno import ArduinoUnoBoard

USB_ID: Set[Tuple[int, int]] = {
    (0x2341, 0x0043),  # Fake Uno
    (0x2a03, 0x0043),  # Fake Uno
    (0x1a86, 0x7523),  # Real Uno
}


def is_arduino_uno(port: ListPortInfo) -> bool:
    """Check if a ListPortInfo represents an Arduino Uno."""
    return (port.vid, port.pid) in USB_ID


class ArduinoUnoHardwareBackend(
    SerialHardwareBackend,
):
    """
    Hardware Backend for the Arduino Uno.

    Currently only for the SourceBots Arduino Firmware.
    """

    environment = HardwareEnvironment
    board = ArduinoUnoBoard

    @classmethod
    def discover(
            cls,
            find: Callable = comports,
            serial_class: Type[Serial] = Serial,
    ) -> Set[Board]:
        """Discover all connected motor boards."""
        # Find all serial ports.
        ports: List[ListPortInfo] = find()

        # Get a list of boards from the ports.
        boards: Set[Board] = set()
        for port in filter(is_arduino_uno, ports):
            boards.add(
                ArduinoUnoBoard(
                    "unknown",
                    cls(port.device, serial_class),
                ),
            )

        return boards

    @handle_serial_error
    def __init__(self, serial_port: str, serial_class: Type[Serial] = Serial) -> None:
        super(ArduinoUnoHardwareBackend, self).__init__(
            serial_port=serial_port,
            serial_class=serial_class,
            baud=115200,
        )

        count = 0

        line = self.read_serial_line(empty=True)
        while len(line) == 0:
            line = self.read_serial_line(empty=True)
            count += 1
            if count > 25:
                raise CommunicationError(f"Arduino ({serial_port}) is not responding.")

        if line != "# Booted":
            raise CommunicationError("Arduino Boot Error.")
        self._version_line = self.read_serial_line()

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return self._version_line
