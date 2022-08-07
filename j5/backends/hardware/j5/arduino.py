"""Base backend for Arduino Uno and its derivatives."""

import logging
from abc import abstractmethod
from datetime import timedelta
from threading import Lock
from typing import Mapping, Optional, Set, Tuple, Type

from serial.tools.list_ports_common import ListPortInfo

from j5.backends.hardware.env import NotSupportedByHardwareError
from j5.backends.hardware.j5.serial import SerialHardwareBackend
from j5.boards import Board
from j5.boards.arduino import ArduinoUno
from j5.components import GPIOPinInterface, GPIOPinMode, LEDInterface

LOGGER = logging.getLogger(__name__)


class DigitalPinData:
    """Contains data about a digital pin."""

    mode: GPIOPinMode
    state: bool

    def __init__(self, *, mode: GPIOPinMode, state: bool):
        self.mode = mode
        self.state = state


class ArduinoHardwareBackend(
    LEDInterface,
    GPIOPinInterface,
    SerialHardwareBackend,
):
    """An abstract class to create backends for different Arduinos."""

    board: Type[ArduinoUno]
    USB_IDS: Set[Tuple[int, int]] = {
        (0x2341, 0x0043),  # Fake Uno
        (0x2a03, 0x0043),  # Fake Uno
        (0x1a86, 0x7523),  # Real Uno
        (0x10c4, 0xea60),  # Ruggeduino
        (0x16d0, 0x0613),  # Ruggeduino
    }
    DEFAULT_TIMEOUT: timedelta = timedelta(milliseconds=1250)

    @classmethod
    def is_arduino(cls, port: ListPortInfo) -> bool:
        """
        Check if a ListPortInfo represents a valid Arduino derivative.

        :param port: ListPortInfo object.
        :returns: True if object represents valid Arduino derivative.
        """
        return (port.vid, port.pid) in cls.USB_IDS

    @classmethod
    def discover(cls) -> Set[Board]:
        """
        Discover boards that this backend can control.

        :returns: set of boards that this backend can control.
        """
        # Find all serial ports.
        ports = cls.get_comports()

        # Get a list of boards from the ports.
        boards: Set[Board] = set()
        for port in filter(cls.is_arduino, ports):
            if port.serial_number is None:
                LOGGER.warning(
                    "Found Arduino Uno-like device without a serial number. "
                    f"Ignoring device as it is incompatible: {port.usb_info()}",
                )
            else:
                boards.add(
                    cls.board(
                        port.serial_number,
                        cls(port.device),
                    ),
                )

        return boards

    def __init__(
            self,
            serial_port: str,
            baud: int = 115200,
            timeout: timedelta = DEFAULT_TIMEOUT,
    ) -> None:
        super().__init__(
            serial_port=serial_port,
            baud=baud,
            timeout=timeout,
        )

        self.serial_port = serial_port

        self._lock = Lock()

        self._digital_pins: Mapping[int, DigitalPinData] = {
            i: DigitalPinData(mode=GPIOPinMode.DIGITAL_INPUT, state=False)
            for i in range(2, ArduinoUno.FIRST_ANALOGUE_PIN)
        }

    @property
    @abstractmethod
    def firmware_version(self) -> Optional[str]:
        """
        The firmware version reported by the board.

        :returns: firmware version reported by the board, if any.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def _update_digital_pin(self, identifier: int) -> None:
        """
        Write the stored value of a digital pin to the Arduino.

        Reads the state out of self._digital_pins.

        :param identifier: Pin number to update.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def _read_digital_pin(self, identifier: int) -> bool:
        """
        Read the value of a digital pin from the Arduino.

        :param identifier: pin number to read value of.
        :returns: state of the pin.
        """
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def _read_analogue_pin(self, identifier: int) -> float:
        """
        Read the value of an analogue pin from the Arduino.

        :param identifier: pin number to read value of.
        :returns: analogue value of the pin.
        """
        raise NotImplementedError  # pragma: nocover

    def set_gpio_pin_mode(self, identifier: int, pin_mode: GPIOPinMode) -> None:
        """
        Set the hardware mode of a GPIO pin.

        :param identifier: pin number to set.
        :param pin_mode: mode to set the pin to.
        :raises NotSupportedByHardwareError: function not supported.
        """
        digital_pin_modes = {
            GPIOPinMode.DIGITAL_INPUT,
            GPIOPinMode.DIGITAL_INPUT_PULLUP,
            GPIOPinMode.DIGITAL_OUTPUT,
        }
        if identifier < ArduinoUno.FIRST_ANALOGUE_PIN:
            # Digital pin
            if pin_mode in digital_pin_modes:
                self._digital_pins[identifier].mode = pin_mode
                self._update_digital_pin(identifier)
                return
        else:
            # Analogue pin
            if pin_mode is GPIOPinMode.ANALOGUE_INPUT:
                return
        raise NotSupportedByHardwareError(
            f"{self.board.name} does not support mode {pin_mode} on pin {identifier}.",
        )

    def get_gpio_pin_mode(self, identifier: int) -> GPIOPinMode:
        """
        Get the hardware mode of a GPIO pin.

        :param identifier: pin number.
        :returns: mode of the pin.
        """
        if identifier < ArduinoUno.FIRST_ANALOGUE_PIN:
            return self._digital_pins[identifier].mode

        return GPIOPinMode.ANALOGUE_INPUT

    def write_gpio_pin_digital_state(self, identifier: int, state: bool) -> None:
        """
        Write to the digital state of a GPIO pin.

        :param identifier: pin number
        :param state: desired digital state.
        :raises ValueError: pin is not in correct mode.
        :raises NotSupportedByHardwareError: function not supported.
        """
        if identifier >= ArduinoUno.FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Digital functions not supported on analogue pins",
            )
        if self._digital_pins[identifier].mode is not GPIOPinMode.DIGITAL_OUTPUT:
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_OUTPUT "
                             f"in order to set the digital state.")
        self._digital_pins[identifier].state = state
        self._update_digital_pin(identifier)

    def get_gpio_pin_digital_state(self, identifier: int) -> bool:
        """
        Get the last written state of a given GPIO pin.

        :param identifier: pin number
        :returns: Last known digital state of the pin.
        :raises ValueError: pin is not in correct mode.
        :raises NotSupportedByHardwareError: function not supported.
        """
        if identifier >= ArduinoUno.FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Digital functions not supported on analogue pins.",
            )
        if self._digital_pins[identifier].mode is not GPIOPinMode.DIGITAL_OUTPUT:
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_OUTPUT "
                             f"in order to read the digital state.")
        return self._digital_pins[identifier].state

    def read_gpio_pin_digital_state(self, identifier: int) -> bool:
        """
        Read the digital state of the GPIO pin.

        :param identifier: pin number
        :returns: digital state of the pin.
        :raises ValueError: pin is not in correct mode.
        :raises NotSupportedByHardwareError: function not supported.
        """
        if identifier >= ArduinoUno.FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Digital functions not supported on analogue pins.",
            )
        if self._digital_pins[identifier].mode not in (
            GPIOPinMode.DIGITAL_INPUT,
            GPIOPinMode.DIGITAL_INPUT_PULLUP,
        ):
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_INPUT_* "
                             f"in order to read the digital state.")
        return self._read_digital_pin(identifier)

    def read_gpio_pin_analogue_value(self, identifier: int) -> float:
        """
        Read the scaled analogue value of the GPIO pin.

        :param identifier: pin number
        :returns: scaled analogue value of the pin.
        :raises NotSupportedByHardwareError: function not supported.
        """
        if identifier < ArduinoUno.FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Analogue functions not supported on digital pins.",
            )
        return self._read_analogue_pin(identifier)

    def write_gpio_pin_dac_value(self, identifier: int, scaled_value: float) -> None:
        """
        Write a scaled analogue value to the DAC on the GPIO pin.

        :param identifier: pin number
        :param scaled_value: scaled analogue value to write
        :raises NotSupportedByHardwareError: Arduino Uno does not have a DAC.
        """
        raise NotSupportedByHardwareError(f"{self.board.name} does not have a DAC.")

    def write_gpio_pin_pwm_value(self, identifier: int, duty_cycle: float) -> None:
        """
        Write a scaled analogue value to the PWM on the GPIO pin.

        :param identifier: pin number
        :param duty_cycle: duty cycle to writee
        :raises NotSupportedByHardwareError: Not implemented in  supported firmware yet.
        """
        raise NotSupportedByHardwareError(
            f"{self.board.name} firmware does not implement PWM output.",
        )

    def get_led_state(self, identifier: int) -> bool:
        """
        Get the state of an LED.

        :param identifier: LED identifier.
        :returns: current state of the LED.
        :raises ValueError: invalid LED identifier.
        """
        if identifier != 0:
            raise ValueError(f"{self.board.name} only has LED 0 (digital pin 13).")
        return self.get_gpio_pin_digital_state(13)

    def set_led_state(self, identifier: int, state: bool) -> None:
        """
        Set the state of an LED.

        :param identifier: LED identifier.
        :param state: desired state of the LED.
        :raises ValueError: invalid LED identifier.
        """
        if identifier != 0:
            raise ValueError(f"{self.board.name} only has LED 0 (digital pin 13).")
        self.write_gpio_pin_digital_state(13, state)
