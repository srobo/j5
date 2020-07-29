"""Student Robotics Ruggeduino Hardware Implementation."""

from typing import Optional, Type

from serial import Serial, SerialException, SerialTimeoutException

from j5.backends import CommunicationError
from j5.backends.hardware import NotSupportedByHardwareError
from j5.backends.hardware.j5.arduino import ArduinoHardwareBackend
from j5.boards.sr.v4.ruggeduino import Ruggeduino
from j5.components import GPIOPinMode, StringCommandComponentInterface


class SRV4RuggeduinoHardwareBackend(
    StringCommandComponentInterface,
    ArduinoHardwareBackend,
):
    """
    Hardware Backend for the Ruggeduino SE.

    Supports Student Robotics' ruggeduino firmware and teams' custom firmware.
    """

    board = Ruggeduino

    def __init__(
            self,
            serial_port: str,
            serial_class: Type[Serial] = Serial,
    ):
        super(SRV4RuggeduinoHardwareBackend, self).__init__(
            serial_port=serial_port,
            serial_class=serial_class,
        )

        # Verify that the Ruggeduino has booted
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
        self._version_line = line

        # Verify the firmware version
        if int(self.firmware_version) != 1:
            raise CommunicationError(
                f"Unexpected firmware version: {self.firmware_version}, "
                f"expected \"1\".",
            )

        for pin_number in self._digital_pins.keys():
            self.set_gpio_pin_mode(pin_number, GPIOPinMode.DIGITAL_INPUT)

    @property
    def firmware_version(self) -> str:
        """The firmware version of the board."""
        return self._version_line.split(":")[-1]

    @property
    def is_official_firmware(self) -> bool:
        """The type of firmware on the board."""
        return self._version_line.split(":")[0] == "SRduino"

    def _command(self, command: str, pin: Optional[int] = None) -> str:
        """Send a command to the board."""
        if len(command) != 1:
            raise RuntimeError("Commands should be 1 character long.")

        return self._execute_raw_string_command(command + self.encode_pin(pin))

    @staticmethod
    def encode_pin(pin: Optional[int]) -> str:
        """Encode a pin number as a letter of the alphabet."""
        return chr(ord('a') + pin) if pin is not None else ""

    def _update_digital_pin(self, identifier: int) -> None:
        if identifier >= Ruggeduino.FIRST_ANALOGUE_PIN:
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
        result_map = {"h": True, "l": False}
        if result in result_map:
            return result_map[result]

        raise CommunicationError(f"Invalid response from Ruggeduino: {result!r}")

    def _read_analogue_pin(self, identifier: int) -> float:
        """Read the value of an analogue pin from the Arduino."""
        if identifier >= Ruggeduino.FIRST_ANALOGUE_PIN + 6:
            raise NotSupportedByHardwareError(
                "Ruggeduino firmware only has 6 analogue inputs (IDs 14-19)",
            )
        result = self._command("a", identifier - 14)
        return (int(result) / 1024.0) * 5.0

    def execute_string_command(self, command: str) -> str:
        """Send a string command to the Ruggeduino and return the result."""
        if self.is_official_firmware:
            raise NotSupportedByHardwareError(
                "Ruggeduino should run custom firmware for command support",
            )
        return self._execute_raw_string_command(command)

    def _execute_raw_string_command(self, command: str) -> str:
        """Send a raw string command to the Ruggeduino and return the result."""
        try:
            with self._lock:
                self._serial.write(command.encode("utf-8"))
                # Get all the characters in the input buffer
                return self.read_serial_line(empty=True)
        except SerialTimeoutException as e:
            raise CommunicationError(f"Serial Timeout Error: {e}") from e
        except SerialException as e:
            raise CommunicationError(f"Serial Error: {e}") from e
