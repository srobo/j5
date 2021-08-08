"""Base backend for Arduino Uno and its derivatives."""

from typing import Mapping, Optional, Type

from j5.backends import Backend
from j5.backends.console import Console
from j5.components import GPIOPinInterface, GPIOPinMode, LEDInterface


class PinData:
    """Contains data about a pin."""

    mode: GPIOPinMode
    digital_state: bool

    def __init__(self, *, mode: GPIOPinMode, digital_state: bool):
        self.mode = mode
        self.digital_state = digital_state


class ArduinoConsoleBackend(
    GPIOPinInterface,
    LEDInterface,
    Backend,
):
    """An abstract class to create console backends for different Arduinos."""

    def __init__(self, serial: str, console_class: Type[Console] = Console) -> None:
        self._serial = serial

        self._pins: Mapping[int, PinData] = {
            i: PinData(mode=GPIOPinMode.DIGITAL_OUTPUT, digital_state=False)
            for i in range(2, 20)
            # Digital 2 - 13
            # Analogue 14 - 19
        }

        # Setup console helper
        self._console = console_class(f"{self.board.__name__}({self._serial})")

    @property
    def firmware_version(self) -> Optional[str]:
        """
        The firmware version reported by the board.

        :returns: firmware version reported by the board, if any.
        """
        return None  # Console, so no firmware

    def set_gpio_pin_mode(self, identifier: int, pin_mode: GPIOPinMode) -> None:
        """
        Set the hardware mode of a GPIO pin.

        :param identifier: pin number to set.
        :param pin_mode: mode to set the pin to.
        """
        self._console.info(f"Set pin {identifier} to {pin_mode.name}")
        self._pins[identifier].mode = pin_mode

    def get_gpio_pin_mode(self, identifier: int) -> GPIOPinMode:
        """
        Get the hardware mode of a GPIO pin.

        :param identifier: pin number.
        :returns: mode of the pin.
        """
        return self._pins[identifier].mode

    def write_gpio_pin_digital_state(self, identifier: int, state: bool) -> None:
        """
        Write to the digital state of a GPIO pin.

        :param identifier: pin number
        :param state: desired digital state.
        :raises ValueError: pin is not in correct mode.
        """
        if self._pins[identifier].mode is not GPIOPinMode.DIGITAL_OUTPUT:
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_OUTPUT "
                             f"in order to set the digital state.")
        self._console.info(f"Set pin {identifier} state to {state}")
        self._pins[identifier].digital_state = state

    def get_gpio_pin_digital_state(self, identifier: int) -> bool:
        """
        Get the last written state of a given GPIO pin.

        :param identifier: pin number
        :returns: Last known digital state of the pin.
        :raises ValueError: pin is not in correct mode.
        """
        if self._pins[identifier].mode is not GPIOPinMode.DIGITAL_OUTPUT:
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_OUTPUT "
                             f"in order to read the digital state.")
        return self._pins[identifier].digital_state

    def read_gpio_pin_digital_state(self, identifier: int) -> bool:
        """
        Read the digital state of a given GPIO pin.

        :param identifier: pin number
        :returns: digital state of the pin.
        :raises ValueError: pin is not in correct mode.
        """
        if self._pins[identifier].mode not in [
            GPIOPinMode.DIGITAL_INPUT_PULLUP,
            GPIOPinMode.DIGITAL_INPUT,
            GPIOPinMode.DIGITAL_INPUT_PULLDOWN,
        ]:
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_INPUT_* "
                             f"in order to read the digital state.")
        return self._console.read(f"Pin {identifier} digital state [true/false]", bool)

    def read_gpio_pin_analogue_value(self, identifier: int) -> float:
        """
        Read the scaled analogue value of a given GPIO pin.

        :param identifier: pin number
        :returns: scaled analogue value of the pin.
        :raises ValueError: pin is not in correct mode.
        """
        if self._pins[identifier].mode is not GPIOPinMode.ANALOGUE_INPUT:
            raise ValueError(f"Pin {identifier} mode needs to be ANALOGUE_INPUT "
                             f"in order to read the analogue value.")
        return self._console.read(f"Pin {identifier} ADC state [float]", float)

    def write_gpio_pin_dac_value(self, identifier: int, scaled_value: float) -> None:
        """
        Write a scaled analogue value to the DAC on a given GPIO pin.

        :param identifier: pin number
        :param scaled_value: scaled analogue value to write
        :raises NotImplementedError: Arduino Uno does not have a DAC.
        """
        # Uno doesn't have any of these.
        raise NotImplementedError

    def write_gpio_pin_pwm_value(self, identifier: int, duty_cycle: float) -> None:
        """
        Write a scaled analogue value to the PWM on a given GPIO pin.

        :param identifier: pin number
        :param duty_cycle: duty cycle to write
        :raises NotImplementedError: Not implemented in any supported firmware yet.
        """
        # Not implemented on derivitive boards yet.
        raise NotImplementedError

    def get_led_state(self, identifier: int) -> bool:
        """
        Get the state of an LED.

        :param identifier: LED identifier.
        :returns: current state of the LED.
        :raises ValueError: invalid LED identifier.
        """
        if identifier != 0:
            raise ValueError("Arduino Uno only has LED 0 (digital pin 13).")
        return self.get_gpio_pin_digital_state(13)

    def set_led_state(self, identifier: int, state: bool) -> None:
        """
        Set the state of an LED.

        :param identifier: LED identifier.
        :param state: desired state of the LED.
        :raises ValueError: invalid LED identifier.
        """
        if identifier != 0:
            raise ValueError("Arduino Uno only has LED 0 (digital pin 13)")
        self.write_gpio_pin_digital_state(13, state)
