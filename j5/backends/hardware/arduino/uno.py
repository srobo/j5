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
from j5.components import GPIOPinInterface, GPIOPinMode, LEDInterface

USB_IDS: Set[Tuple[int, int]] = {
    (0x2341, 0x0043),  # Fake Uno
    (0x2a03, 0x0043),  # Fake Uno
    (0x1a86, 0x7523),  # Real Uno
}


def is_arduino_uno(port: ListPortInfo) -> bool:
    """Check if a ListPortInfo represents an Arduino Uno."""
    return (port.vid, port.pid) in USB_IDS


class ArduinoUnoHardwareBackend(
    LEDInterface,
    GPIOPinInterface,
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
                    port.serial_number,
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

        self._pins = {
            i: GPIOPinMode.DIGITAL_INPUT
            for i in range(2, 20)
            # Digital 2 - 13
            # Analogue 14 - 19
        }

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

        if self.firmware_version is not None:
            version_ids = self.firmware_version.split(".")
        else:
            version_ids = ["0", "0", "0"]

        if int(version_ids[0]) < 2019 or int(version_ids[1]) < 6:
            raise CommunicationError(
                f"Unexpected firmware version: {self.firmware_version},",
                f" expected at least: \"2019.6.0\".",
            )

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return self._version_line.split("v")[1]

    def _command(self, command: str, params: List[str]) -> str:
        """Send a command to the board."""

    def set_gpio_pin_mode(self, identifier: int, pin_mode: GPIOPinMode) -> None:
        """Set the hardware mode of a GPIO pin."""
        self._pins[identifier] = pin_mode

    def get_gpio_pin_mode(self, identifier: int) -> GPIOPinMode:
        """Get the hardware mode of a GPIO pin."""
        return self._pins[identifier]

    def write_gpio_pin_digital_state(self, identifier: int, state: bool) -> None:
        """Write to the digital state of a GPIO pin."""

    def get_gpio_pin_digital_state(self, identifier: int) -> bool:
        """Get the last written state of the GPIO pin."""
        return False

    def read_gpio_pin_digital_state(self, identifier: int) -> bool:
        """Read the digital state of the GPIO pin."""
        return False

    def read_gpio_pin_analogue_value(self, identifier: int) -> float:
        """Read the scaled analogue value of the GPIO pin."""
        return 0.0

    def write_gpio_pin_dac_value(self, identifier: int, scaled_value: float) -> None:
        """Write a scaled analogue value to the DAC on the GPIO pin."""
        # Uno doesn't have any of these.
        raise NotImplementedError

    def write_gpio_pin_pwm_value(self, identifier: int, duty_cycle: float) -> None:
        """Write a scaled analogue value to the PWM on the GPIO pin."""
        # Not implemented on ArduinoUnoBoard yet.
        raise NotImplementedError

    def get_led_state(self, identifier: int) -> bool:
        """Get the state of an LED."""
        return False

    def set_led_state(self, identifier: int, state: bool) -> None:
        """Set the state of an LED."""
