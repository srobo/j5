"""Student Robotics Ruggeduino Hardware Implementation."""
from datetime import timedelta
from enum import Enum
from threading import Lock
from typing import Set, Tuple, Callable, Type, List, Mapping, Optional

from serial import Serial
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo

from j5.backends import CommunicationError
from j5.backends.hardware.j5.serial import SerialHardwareBackend, handle_serial_error
from j5.boards import Board
from j5.boards.sr.v4.ruggeduino import SRRuggeduinoBoard

from j5.components import GPIOPinMode, LEDInterface, GPIOPinInterface

FIRST_ANALOGUE_PIN = 14


def is_ruggeduino(port: ListPortInfo) -> bool:
    return (port.vid, port.pid) == (0x10c4, 0xea60)  # From the CP2104 datasheet, I don't know if this is right


def encode_pin(pin):
    """Encode a pin number as a letter of the alphabet."""
    return chr(ord('a') + pin)


class DigitalPinData:
    """Contains data about a digital pin."""

    mode: GPIOPinMode
    state: bool

    def __init__(self, *, mode: GPIOPinMode, state: bool):
        self.mode = mode
        self.state = state


class FirmwareTypeEnum(Enum):
    OFFICIAL = "SRduino"  # Unmodified firmware
    CUSTOM = "SRcustom"  # Official, with added commands
    OTHER = "SRother"  # Bespoke firmware


class SRRuggeduinoHardwareBackend(
    LEDInterface,
    GPIOPinInterface,
    SerialHardwareBackend,
):
    """
    Hardware Backend for the Ruggeduino ET.

    Supports Student Robotics ruggeduino firmware and teams' custom firmware.
    """

    board = SRRuggeduinoBoard

    @classmethod
    def discover(
            cls,
            comports: Callable = comports,
            serial_class: Type[Serial] = Serial,
    ) -> Set[Board]:
        """Discover all connected ruggeduino boards."""
        # Find all serial ports.
        ports: List[ListPortInfo] = comports()

        boards: Set[Board] = set()
        for port in filter(is_ruggeduino, ports):
            boards.add(
                SRRuggeduinoBoard(
                    port.serial_number,
                    cls(port.device, serial_class)
                ),
            )

        return boards

    @handle_serial_error
    def __init__(self, serial_port: str, serial_class: Type[Serial] = Serial) -> None:
        super(SRRuggeduinoHardwareBackend, self).__init__(
            serial_port=serial_port,
            serial_class=serial_class,
            baud=115200,
            timeout=timedelta(milliseconds=1250)
        )

        self._lock = Lock()

        self._digital_pins: Mapping[int, DigitalPinData] = {
            i: DigitalPinData(mode=GPIOPinMode.DIGITAL_INPUT, state=False)
            for i in range(2, FIRST_ANALOGUE_PIN)
        }

        # This only works if the firmware supports the SRduino verson command
        with self._lock:
            count = 0
            self._command("v")
            line = self.read_serial_line(empty=True)
            while len(line) == 0:
                self._command("v")
                line = self.read_serial_line(empty=True)
                count += 1
                if count > 25:
                    raise CommunicationError(
                        f"Ruggeduino ({serial_port}) is not responding.",
                    )

            self._version_line = self.read_serial_line()

        for pin_number in self._digital_pins.keys():
            self.set_gpio_pin_mode(pin_number, GPIOPinMode.DIGITAL_INPUT)

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return self._version_line.split(":")[-1]  # -1 avoids IndexErrors on modified boards

    @property
    def firmware_type(self) -> Optional[FirmwareTypeEnum]:
        """The type of firmware on the board."""
        flavour: str = self._version_line.split(":")[0]
        if flavour == FirmwareTypeEnum.OFFICIAL:
            return FirmwareTypeEnum.OFFICIAL
        elif flavour == FirmwareTypeEnum.CUSTOM:
            return FirmwareTypeEnum.CUSTOM  # Although we can't always trust this
        else:
            return FirmwareTypeEnum.OTHER

    @handle_serial_error
    def _command(self, command: str, pin: str = "") -> str:
        """Send a command to the board."""
        if len(command) != 1:
            raise RuntimeError("Commands are 1 character long")

        with self._lock:
            message: str = command + pin
            self._serial.write(message.encode("utf-8"))

            return self.read_serial_line(empty=True)
