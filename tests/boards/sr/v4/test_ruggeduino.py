"""Tests for the Ruggeduino board."""

import pytest

from j5.backends import Backend
from j5.boards import Board
from j5.boards.arduino import ArduinoUno
from j5.boards.sr.v4.ruggeduino import Ruggeduino
from j5.components import (
    LED,
    GPIOPin,
    GPIOPinInterface,
    GPIOPinMode,
    LEDInterface,
    StringCommandComponent,
    StringCommandComponentInterface,
)


class MockRuggeduinoBackend(
    GPIOPinInterface,
    LEDInterface,
    StringCommandComponentInterface,
    Backend,
):
    """Mock Backend for testing the Student Robotics Ruggeduino."""

    board = Ruggeduino

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

    def execute_string_command(self, command: str) -> str:
        """Send a string command to the Ruggeduino and return the result."""
        return command[::-1]

    @classmethod
    def discover(cls) -> set['Board']:
        """Discover boards."""
        return set()

    @property
    def firmware_version(self) -> str | None:
        """Get the firmware version."""
        return None


def test_ruggeduino_initialisation() -> None:
    """Test that we can initialise a Ruggeduino."""
    Ruggeduino("SERIAL0", MockRuggeduinoBackend())


def test_ruggeduino_analogue_pin() -> None:
    """Test that AnaloguePin has the required values."""
    assert Ruggeduino.AnaloguePin is ArduinoUno.AnaloguePin


def test_ruggeduino_name() -> None:
    """Test the name attribute of the Ruggeduino."""
    ruggeduino = Ruggeduino("SERIAL0", MockRuggeduinoBackend())

    assert ruggeduino.name == "Ruggeduino"


def test_ruggeduino_serial_number() -> None:
    """Test the serial_number attribute of the Ruggeduino."""
    ruggeduino = Ruggeduino("SERIAL0", MockRuggeduinoBackend())

    assert ruggeduino.serial_number == "SERIAL0"


def test_ruggeduino_firmware_version() -> None:
    """Test the firmware_version attribute of the Ruggeduino."""
    ruggeduino = Ruggeduino("SERIAL0", MockRuggeduinoBackend())

    assert ruggeduino.firmware_version is None


def test_ruggeduino_pins() -> None:
    """Test the pins of the Ruggeduino."""
    ruggeduino = Ruggeduino("SERIAL0", MockRuggeduinoBackend())

    assert len(ruggeduino.pins) == 12 + 6

    for i in range(2, 14):
        assert isinstance(ruggeduino.pins[i], GPIOPin)

    for j in Ruggeduino.AnaloguePin:
        assert isinstance(ruggeduino.pins[j], GPIOPin)


def test_pin_mutability() -> None:
    """
    Test the mutability of GPIOPins.

    Ensures that GPIOPin objects cannot be lost.
    """
    ruggeduino = Ruggeduino("SERIAL0", MockRuggeduinoBackend())

    with pytest.raises(TypeError):
        ruggeduino.pins[2] = True  # type: ignore


def test_ruggeduino_make_safe() -> None:
    """Test the make_safe method of the Ruggeduino."""
    ruggeduino = Ruggeduino("SERIAL0", MockRuggeduinoBackend())
    ruggeduino.make_safe()


def test_ruggeduino_supported_components() -> None:
    """Test that the Ruggeduino supports the required components."""
    assert {
        GPIOPin,
        LED,
        StringCommandComponent,
    }.issubset(Ruggeduino.supported_components())


def test_ruggeduino_command() -> None:
    """Test that the Ruggeduino has a serial command component."""
    ruggeduino = Ruggeduino("Serial0", MockRuggeduinoBackend())

    assert isinstance(ruggeduino.command, StringCommandComponent)
