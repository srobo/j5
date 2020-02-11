"""Console Backend for the SourceBots Arduino."""
from datetime import timedelta
from typing import Mapping, Optional, Set, Type, cast

from j5.backends import Backend
from j5.backends.console import Console
from j5.boards import Board
from j5.boards.sb import SBArduinoBoard
from j5.components import GPIOPinInterface, GPIOPinMode, LEDInterface
from j5.components.derived import UltrasoundInterface


class PinData:
    """Contains data about a pin."""

    mode: GPIOPinMode
    digital_state: bool

    def __init__(self, *, mode: GPIOPinMode, digital_state: bool):
        self.mode = mode
        self.digital_state = digital_state


class SBArduinoConsoleBackend(
    GPIOPinInterface,
    LEDInterface,
    UltrasoundInterface,
    Backend,
):
    """Console Backend for the SourceBots Arduino."""

    board = SBArduinoBoard

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover boards that this backend can control."""
        return {cast(Board, SBArduinoBoard("SERIAL", cls("SERIAL")))}

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
        """The firmware version reported by the board."""
        return None  # Console, so no firmware

    def set_gpio_pin_mode(self, identifier: int, pin_mode: GPIOPinMode) -> None:
        """Set the hardware mode of a GPIO pin."""
        self._console.info(f"Set pin {identifier} to {pin_mode.name}")
        self._pins[identifier].mode = pin_mode

    def get_gpio_pin_mode(self, identifier: int) -> GPIOPinMode:
        """Get the hardware mode of a GPIO pin."""
        return self._pins[identifier].mode

    def write_gpio_pin_digital_state(self, identifier: int, state: bool) -> None:
        """Write to the digital state of a GPIO pin."""
        if self._pins[identifier].mode is not GPIOPinMode.DIGITAL_OUTPUT:
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_OUTPUT"
                             f"in order to set the digital state.")
        self._console.info(f"Set pin {identifier} state to {state}")
        self._pins[identifier].digital_state = state

    def get_gpio_pin_digital_state(self, identifier: int) -> bool:
        """Get the last written state of the GPIO pin."""
        if self._pins[identifier].mode is not GPIOPinMode.DIGITAL_OUTPUT:
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_OUTPUT"
                             f"in order to read the digital state.")
        return self._pins[identifier].digital_state

    def read_gpio_pin_digital_state(self, identifier: int) -> bool:
        """Read the digital state of the GPIO pin."""
        if self._pins[identifier].mode not in [
            GPIOPinMode.DIGITAL_INPUT_PULLUP,
            GPIOPinMode.DIGITAL_INPUT,
            GPIOPinMode.DIGITAL_INPUT_PULLDOWN,
        ]:
            raise ValueError(f"Pin {identifier} mode needs to be DIGITAL_INPUT_*"
                             f"in order to read the digital state.")
        return self._console.read(f"Pin {identifier} digital state [true/false]", bool)

    def read_gpio_pin_analogue_value(self, identifier: int) -> float:
        """Read the scaled analogue value of the GPIO pin."""
        if self._pins[identifier].mode is not GPIOPinMode.ANALOGUE_INPUT:
            raise ValueError(f"Pin {identifier} mode needs to be ANALOGUE_INPUT",
                             f"in order to read the digital state.")
        return self._console.read(f"Pin {identifier} ADC state [float]", float)

    def write_gpio_pin_dac_value(self, identifier: int, scaled_value: float) -> None:
        """Write a scaled analogue value to the DAC on the GPIO pin."""
        # Uno doesn't have any of these.
        raise NotImplementedError

    def write_gpio_pin_pwm_value(self, identifier: int, duty_cycle: float) -> None:
        """Write a scaled analogue value to the PWM on the GPIO pin."""
        # Not implemented on SBArduinoBoard yet.
        raise NotImplementedError

    def get_led_state(self, identifier: int) -> bool:
        """Get the state of an LED."""
        if identifier != 0:
            raise ValueError("Arduino Uno only has LED 0 (digital pin 13).")
        return self.get_gpio_pin_digital_state(13)

    def set_led_state(self, identifier: int, state: bool) -> None:
        """Set the state of an LED."""
        if identifier != 0:
            raise ValueError("Arduino Uno only has LED 0 (digital pin 13)")
        self.write_gpio_pin_digital_state(13, state)

    def get_ultrasound_pulse(
            self,
            trigger_pin_identifier: int,
            echo_pin_identifier: int,
    ) -> Optional[timedelta]:
        """
        Get a timedelta for the ultrasound time.

        Returns None if the sensor times out.
        """
        microseconds = self._console.read(
            f"Response time for ultrasound sensor on pins "
            f"{trigger_pin_identifier}/{echo_pin_identifier} [microseconds]",
            float,
        )
        self._update_ultrasound_pin_modes(trigger_pin_identifier, echo_pin_identifier)
        return timedelta(microseconds=microseconds)

    def get_ultrasound_distance(
            self,
            trigger_pin_identifier: int,
            echo_pin_identifier: int,
    ) -> Optional[float]:
        """Get a distance in metres."""
        metres = self._console.read(
            f"Distance for ultrasound sensor on pins "
            f"{trigger_pin_identifier}/{echo_pin_identifier} [metres]",
            float,
        )
        self._update_ultrasound_pin_modes(trigger_pin_identifier, echo_pin_identifier)
        return metres

    def _update_ultrasound_pin_modes(
        self,
        trigger_pin_identifier: int,
        echo_pin_identifier: int,
    ) -> None:
        # Ultrasound functions force the pins into particular modes.
        self._pins[trigger_pin_identifier].mode = GPIOPinMode.DIGITAL_OUTPUT
        self._pins[trigger_pin_identifier].digital_state = False
        self._pins[echo_pin_identifier].mode = GPIOPinMode.DIGITAL_INPUT
