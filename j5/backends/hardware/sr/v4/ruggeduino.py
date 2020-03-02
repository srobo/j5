"""Student Robotics Ruggeduino Hardware Implementation."""

from datetime import timedelta
from enum import Enum
from threading import Lock
from typing import Callable, List, Mapping, Optional, Set, Type

from serial import Serial, SerialException, SerialTimeoutException
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo

from j5.backends import CommunicationError
from j5.backends.hardware.env import NotSupportedByHardwareError
from j5.backends.hardware.j5.serial import SerialHardwareBackend
from j5.boards import Board
from j5.boards.sr.v4.ruggeduino import Ruggeduino
from j5.components import GPIOPinInterface, GPIOPinMode, LEDInterface

FIRST_ANALOGUE_PIN = 14


def is_ruggeduino(port: ListPortInfo) -> bool:
    """Checks whether a USB device is a Ruggeduino."""
    return (port.vid, port.pid) == (0x10c4, 0xea60)  # For the CP2104 used by Ruggeduino


def encode_pin(pin: int) -> str:
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
    """
    The types of firmware that can be present on the Ruggeduino.

    OFFICIAL - Unmodified firmware. Students probably won't know that the default
               firmware sends this value, unless they pore through j5 or sr-robot.
    CUSTOM - Official, but with added commands. This value is sent by the open version
             of the firmware. This firmware should support all official commands.
    OTHER - Bespoke firmware entirely devised by the students themselves. Compatibility
            should not be assumed.
    """

    OFFICIAL = "SRduino"
    CUSTOM = "SRcustom"
    OTHER = "SRother"


class SRV4RuggeduinoHardwareBackend(
    LEDInterface,
    GPIOPinInterface,
    SerialHardwareBackend,
):
    """
    Hardware Backend for the Ruggeduino SE.

    Supports Student Robotics' ruggeduino firmware and teams' custom firmware.
    """

    board = Ruggeduino

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
                cls.board(
                    port.serial_number,
                    cls(port.device, serial_class),  # type: ignore
                ),
            )

        return boards

    def __init__(
            self,
            serial_port: str,
            serial_class: Type[Serial] = Serial,
    ) -> None:
        super(SRV4RuggeduinoHardwareBackend, self).__init__(
            serial_port=serial_port,
            serial_class=serial_class,
            baud=115200,
            timeout=timedelta(milliseconds=1250),
        )

        self._lock = Lock()

        self._digital_pins: Mapping[int, DigitalPinData] = {
            i: DigitalPinData(mode=GPIOPinMode.DIGITAL_INPUT, state=False)
            for i in range(2, FIRST_ANALOGUE_PIN)
        }

        # This only works if the firmware supports the SRduino verson command.
        # It may have unexpected behaviour on custom firmware.
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
                        f"Ruggeduino ({serial_port}) is not responding "
                        f"or runs custom firmware.",
                    )

            self._version_line = self.read_serial_line()

        for pin_number in self._digital_pins.keys():
            self.set_gpio_pin_mode(pin_number, GPIOPinMode.DIGITAL_INPUT)

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return self._version_line.split(":")[-1]

    @property
    def firmware_type(self) -> Optional[FirmwareTypeEnum]:
        """The type of firmware on the board."""
        flavour: str = self._version_line.split(":")[0]
        if flavour == FirmwareTypeEnum.OFFICIAL.value:
            return FirmwareTypeEnum.OFFICIAL
        elif flavour == FirmwareTypeEnum.CUSTOM.value:
            return FirmwareTypeEnum.CUSTOM
        else:
            return FirmwareTypeEnum.OTHER

    def _command(self, command: str, pin: str = "") -> str:
        """Send a command to the board."""
        if len(command) != 1:
            raise RuntimeError("Commands should be 1 character long")

        try:
            with self._lock:
                message: str = command + pin
                self._serial.write(message.encode("utf-8"))

                return self.read_serial_line(empty=True)
        except SerialTimeoutException as e:
            raise CommunicationError(f"Serial Timeout Error: {e}") from e
        except SerialException as e:
            raise CommunicationError(f"Serial Error: {e}") from e

    def _update_digital_pin(self, identifier: int) -> None:
        if identifier >= FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Digital functions not supported on analogue pins",
            )
        pin: DigitalPinData = self._digital_pins[identifier]
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
            raise RuntimeError(f"Invalid GPIOPinMode for pin {identifier}")
        self._command(command, encode_pin(identifier))

    def set_gpio_pin_mode(self, identifier: int, pin_mode: GPIOPinMode) -> None:
        """Set the hardware mode of a GPIO pin."""
        digital_pin_modes = (
            GPIOPinMode.DIGITAL_INPUT,
            GPIOPinMode.DIGITAL_INPUT_PULLUP,
            GPIOPinMode.DIGITAL_OUTPUT,
        )
        if identifier < FIRST_ANALOGUE_PIN:
            # Digital pin
            if pin_mode in digital_pin_modes:
                self._digital_pins[identifier].mode = pin_mode
                self._update_digital_pin(identifier)
                return
        elif pin_mode is GPIOPinMode.ANALOGUE_INPUT:  # Analogue pin
            return
        else:
            raise NotSupportedByHardwareError(
                f"Ruggeduino does not support mode {pin_mode} on pin {identifier}",
            )

    def get_gpio_pin_mode(self, identifier: int) -> GPIOPinMode:
        """Get the hardware mode of a GPIO pin."""
        if identifier < FIRST_ANALOGUE_PIN:
            return self._digital_pins[identifier].mode
        else:
            return GPIOPinMode.ANALOGUE_INPUT

    def write_gpio_pin_digital_state(self, identifier: int, state: bool) -> None:
        """Write to the digital state of a GPIO pin."""
        if identifier >= FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Digital functions not supported on analogue pins",
            )
        if self._digital_pins[identifier].mode is not GPIOPinMode.DIGITAL_OUTPUT:
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_OUTPUT"
                             f"in order to set the digital state.")
        self._digital_pins[identifier].state = state
        self._update_digital_pin(identifier)

    def get_gpio_pin_digital_state(self, identifier: int) -> bool:
        """Get the last written state of the GPIO pin."""
        if identifier >= FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Digital functions not supported on analogue pins",
            )
        if self._digital_pins[identifier].mode is not GPIOPinMode.DIGITAL_OUTPUT:
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_OUTPUT"
                             f"in order to read the digital state.")
        return self._digital_pins[identifier].state

    def read_gpio_pin_digital_state(self, identifier: int) -> bool:
        """Read the digital state of the GPIO pin."""
        if identifier >= FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Digital functions not supported on analogue pins",
            )
        if self._digital_pins[identifier].mode not in (
            GPIOPinMode.DIGITAL_INPUT,
            GPIOPinMode.DIGITAL_INPUT_PULLUP,
        ):
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_INPUT_*"
                             f"in order to read the digital state.")
        results = self._command("r", str(identifier))
        if len(results) != 1:
            raise CommunicationError(f"Invalid response from Ruggeduino: {results!r}")
        result = results[0]
        if result == "h":
            return True
        elif result == "l":
            return False
        else:
            raise CommunicationError(f"Invalid response from Ruggeduino: {result!r}")

    def read_gpio_pin_analogue_value(self, identifier: int) -> float:
        """Read the analogue voltage of the GPIO pin."""
        if identifier < FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Analogue functions not supported on digital pins",
            )
        analogue_pin_num = identifier - 14
        results = self._command("a")
        for result in results:
            pin_name, reading = result.split(None, 1)
            if pin_name == f"a{analogue_pin_num}":
                voltage = (int(reading) / 1024.0) * 5.0
                return voltage
        raise CommunicationError(f"Invalid response from Ruggeduino: {results!r}")

    def write_gpio_pin_dac_value(self, identifier: int, scaled_value: float) -> None:
        """Write a scaled analogue value to the DAC on the GPIO pin."""
        raise NotSupportedByHardwareError("SR Ruggeduino does not have a DAC")

    def write_gpio_pin_pwm_value(self, identifier: int, duty_cycle: float) -> None:
        """Write a scaled analogue value to the PWM on the GPIO pin."""
        raise NotSupportedByHardwareError(
            "SR Ruggeduino firmware does not implement PWM output",
        )

    def get_led_state(self, identifier: int) -> bool:
        """Get the state of an LED."""
        if identifier != 0:
            raise ValueError("Ruggeduino only has LED 0 (digital pin 13).")
        return self.get_gpio_pin_digital_state(13)

    def set_led_state(self, identifier: int, state: bool) -> None:
        """Set the state of an LED."""
        if identifier != 0:
            raise ValueError("Ruggeduino only has LED 0 (digital pin 13)")
        self.write_gpio_pin_digital_state(13, state)
