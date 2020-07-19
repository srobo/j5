"""Student Robotics Ruggeduino Hardware Implementation."""

from enum import Enum
from typing import Optional, Type

from serial import Serial, SerialException, SerialTimeoutException
from serial.tools.list_ports_common import ListPortInfo

from j5.backends import CommunicationError
from j5.backends.hardware.j5.arduino import ArduinoHardwareBackend
from j5.boards.j5.arduino import FIRST_ANALOGUE_PIN
from j5.boards.sr.v4.ruggeduino import Ruggeduino
from j5.components import GPIOPinMode


def encode_pin(pin: Optional[int]) -> str:
    """Encode a pin number as a letter of the alphabet."""
    if pin is None:
        return ""
    else:
        return chr(ord('a') + pin)


class FirmwareType(Enum):
    """
    The types of firmware that can be present on the Ruggeduino.

    OFFICIAL - Unmodified firmware. Students probably won't know that the default
               firmware sends this value, unless they pore through j5 or sr-robot.
    EXTENDED - Official, but with added commands. This value is sent by the open version
             of the firmware. This firmware should support all official commands.
    CUSTOM - Bespoke firmware entirely devised by the students themselves. Compatibility
            should not be assumed.
    """

    OFFICIAL = "SRduino"
    EXTENDED = "SRcustom"
    CUSTOM = "SRother"


class SRV4RuggeduinoHardwareBackend(ArduinoHardwareBackend):
    """
    Hardware Backend for the Ruggeduino SE.

    Supports Student Robotics' ruggeduino firmware and teams' custom firmware.
    """

    board = Ruggeduino

    @staticmethod
    def is_arduino(port: ListPortInfo) -> bool:
        """Check whether a USB device is a Ruggeduino."""
        return (port.vid, port.pid) == (0x10c4, 0xea60)  # Ruggeduino uses a CP2104

    def __init__(
            self,
            serial_port: str,
            serial_class: Type[Serial] = Serial,

    ) -> None:
        super(SRV4RuggeduinoHardwareBackend, self).__init__(
            serial_port=serial_port,
            serial_class=serial_class,
        )

    def _verify_boot(self) -> str:
        """
        Verify that the Ruggeduino has booted and return its version string.

        This only works if the firmware supports the SRduino verson command.
        It may have unexpected behaviour on custom firmware.
        """
        count = 0
        line = self._command("v")
        while len(line) == 0:
            line = self._command("v")
            count += 1
            if count > 25:
                raise CommunicationError(
                    f"Ruggeduino ({self.serial_port}) is not responding "
                    f"or runs custom firmware.",
                )
        return line

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return self._version_line.split(":")[-1]

    @property
    def firmware_type(self) -> FirmwareType:
        """The type of firmware on the board."""
        flavour: str = self._version_line.split(":")[0]
        if flavour == FirmwareType.OFFICIAL.value:
            return FirmwareType.OFFICIAL
        elif flavour == FirmwareType.EXTENDED.value:
            return FirmwareType.EXTENDED
        else:
            return FirmwareType.CUSTOM

    def _verify_firmware_version(self) -> None:
        """Verify that the Ruggeduino firmware meets or exceeds the minimum version."""
        return

    def _command(self, command: str, pin: Optional[int] = None) -> str:
        """Send a command to the board."""
        if len(command) != 1:
            raise RuntimeError("Commands should be 1 character long.")

        try:
            with self._lock:
                message: str = command + encode_pin(pin)
                self._serial.write(message.encode("utf-8"))

                return self.read_serial_line(empty=True)
        except SerialTimeoutException as e:
            raise CommunicationError(f"Serial Timeout Error: {e}") from e
        except SerialException as e:
            raise CommunicationError(f"Serial Error: {e}") from e

    def _update_digital_pin(self, identifier: int) -> None:
        if identifier >= FIRST_ANALOGUE_PIN:
            raise RuntimeError("Reached an unreachable statement.")
        pin = self._digital_pins[identifier]
        command: str
        if pin.mode == GPIOPinMode.DIGITAL_INPUT:
            command = "i"
        elif pin.mode == GPIOPinMode.DIGITAL_INPUT_PULLUP:
            command = "p"
        elif pin.mode == GPIOPinMode.DIGITAL_OUTPUT:
            if pin.state:
                command = "h"
            else:
                command = "l"
        else:
            raise RuntimeError("Reached an unreachable statement.")
        self._command(command, identifier)

    def _read_digital_pin(self, identifier: int) -> bool:
        """Read the value of a digital pin from the Arduino."""
        results = self._command("r", identifier)
        if len(results) != 1:
            raise CommunicationError(f"Invalid response from Ruggeduino: {results!r}")
        result = results[0]
        if result == "h":
            return True
        elif result == "l":
            return False
        else:
            raise CommunicationError(f"Invalid response from Ruggeduino: {result!r}")

    def _read_analogue_pin(self, identifier: int) -> float:
        """Read the value of an analogue pin from the Arduino."""
        result = self._command("a", identifier - 14)
        return (int(result) / 1024.0) * 5.0
