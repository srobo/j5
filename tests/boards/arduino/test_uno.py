"""Tests for the Arduino Uno base class and related classes."""
from typing import Optional, Set

import pytest

from j5.backends import Backend
from j5.boards import Board
from j5.boards.arduino import ArduinoUno
from j5.components import (
    LED,
    GPIOPin,
    GPIOPinInterface,
    GPIOPinMode,
    LEDInterface,
)


class MockArduinoUnoBackend(
    GPIOPinInterface,
    LEDInterface,
    Backend,
):
    """Mock Backend for testing the Arduino Uno."""

    board = ArduinoUno

    def set_gpio_pin_mode(self, identifier: int, pin_mode: GPIOPinMode) -> None:
        """Set the GPIO pin mode."""

    def get_gpio_pin_mode(self, identifier: int) -> GPIOPinMode:
        """Get the GPIO pin mode."""
        return GPIOPinMode.DIGITAL_OUTPUT

    def write_gpio_pin_digital_state(self, identifier: int, state: bool) -> None:
        """Set the GPIO pin digital state."""

    def get_gpio_pin_digital_state(self, identifier: int) -> bool:
        """Get the GPIO pin digital state."""
        return False

    def read_gpio_pin_digital_state(self, identifier: int) -> bool:
        """Read the GPIO pin digital state."""
        return False

    def read_gpio_pin_analogue_value(self, identifier: int) -> float:
        """Read an analogue value from a GPIO pin."""
        return 0.0

    def write_gpio_pin_dac_value(self, identifier: int, scaled_value: float) -> None:
        """Write a DAC value to the GPIO pin."""
        raise NotImplementedError

    def write_gpio_pin_pwm_value(self, identifier: int, duty_cycle: float) -> None:
        """Write a PWM value to the GPIO pin."""

    def get_led_state(self, identifier: int) -> bool:
        """Get the state of the LED."""
        return self.get_gpio_pin_digital_state(13)

    def set_led_state(self, identifier: int, state: bool) -> None:
        """Set the state of the LED."""
        self.write_gpio_pin_digital_state(13, state)

    @classmethod
    def discover(cls) -> Set['Board']:
        """Discover boards."""
        return set()

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version."""
        return None


def test_uno_initialisation() -> None:
    """Test that we can initialise an Uno."""
    ArduinoUno("SERIAL0", MockArduinoUnoBackend())


def test_uno_discover() -> None:
    """Test that we can discover Unos."""
    assert MockArduinoUnoBackend.discover() == set()


def test_uno_analogue_pin() -> None:
    """Test that AnaloguePin has the required values."""
    assert ArduinoUno.FIRST_ANALOGUE_PIN is ArduinoUno.AnaloguePin.A0
    assert ArduinoUno.AnaloguePin.A0.value == 14
    assert ArduinoUno.AnaloguePin.A5.value == 19
    assert len(ArduinoUno.AnaloguePin) == 6


def test_uno_name() -> None:
    """Test the name attribute of the Uno."""
    uno = ArduinoUno("SERIAL0", MockArduinoUnoBackend())

    assert uno.name == "Arduino Uno"


def test_uno_led() -> None:
    """Test the LED of the Uno."""
    uno = ArduinoUno("SERIAL0", MockArduinoUnoBackend())

    assert isinstance(uno.led, LED)


def test_uno_serial() -> None:
    """Test the serial attribute of the Uno."""
    uno = ArduinoUno("SERIAL0", MockArduinoUnoBackend())

    assert uno.serial == "SERIAL0"


def test_uno_firmware_version() -> None:
    """Test the firmware_version attribute of the Uno."""
    uno = ArduinoUno("SERIAL0", MockArduinoUnoBackend())

    assert uno.firmware_version is None


def test_uno_pins() -> None:
    """Test the pins of the Uno."""
    uno = ArduinoUno("SERIAL0", MockArduinoUnoBackend())

    assert len(uno.pins) == 12 + 6

    for i in range(2, 14):
        assert isinstance(uno.pins[i], GPIOPin)

    for j in ArduinoUno.AnaloguePin:
        assert isinstance(uno.pins[j], GPIOPin)


def test_pin_mutability() -> None:
    """
    Test the mutability of GPIOPins.

    Ensures that GPIOPin objects cannot be lost.
    """
    uno = ArduinoUno("SERIAL0", MockArduinoUnoBackend())

    with pytest.raises(TypeError):
        uno.pins[2] = True  # type: ignore


def test_uno_make_safe() -> None:
    """Test the make_safe method of the Uno."""
    uno = ArduinoUno("SERIAL0", MockArduinoUnoBackend())
    uno.make_safe()
