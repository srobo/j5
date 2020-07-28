"""Tests for the SourceBots Arduino and related classes."""

from datetime import timedelta
from typing import TYPE_CHECKING, Optional, Set

import pytest

from j5.backends import Backend
from j5.boards.arduino import ArduinoUno
from j5.boards.sb import SBArduinoBoard
from j5.components import (
    LED,
    GPIOPin,
    GPIOPinInterface,
    GPIOPinMode,
    LEDInterface,
)
from j5.components.derived import UltrasoundInterface, UltrasoundSensor

if TYPE_CHECKING:
    from j5.boards import Board  # noqa


class MockSBArduinoBackend(
    GPIOPinInterface,
    LEDInterface,
    UltrasoundInterface,
    Backend,
):
    """Mock Backend for testing the SourceBots Arduino Uno."""

    board = SBArduinoBoard

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

    def get_ultrasound_pulse(
        self,
        trigger_pin_identifier: int,
        echo_pin_identifier: int,
    ) -> Optional[timedelta]:
        """Get a timedelta for the ultrasound time."""
        return timedelta(milliseconds=3)

    def get_ultrasound_distance(
        self,
        trigger_pin_identifier: int,
        echo_pin_identifier: int,
    ) -> Optional[float]:
        """Get a distance in metres."""
        return 1.0

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
    SBArduinoBoard("SERIAL0", MockSBArduinoBackend())


def test_uno_analogue_pin() -> None:
    """Test that the class doesn't change AnaloguePin."""
    assert SBArduinoBoard.AnaloguePin is ArduinoUno.AnaloguePin


def test_uno_name() -> None:
    """Test the name attribute of the Uno."""
    uno = SBArduinoBoard("SERIAL0", MockSBArduinoBackend())

    assert uno.name == "Arduino Uno"


def test_uno_serial_number() -> None:
    """Test the serial attribute of the Uno."""
    uno = SBArduinoBoard("SERIAL0", MockSBArduinoBackend())

    assert uno.serial_number == "SERIAL0"


def test_uno_firmware_version() -> None:
    """Test the firmware_version attribute of the Uno."""
    uno = SBArduinoBoard("SERIAL0", MockSBArduinoBackend())

    assert uno.firmware_version is None


def test_uno_pins() -> None:
    """Test the pins of the Uno."""
    uno = SBArduinoBoard("SERIAL0", MockSBArduinoBackend())

    assert len(uno.pins) == 12 + 6

    for i in range(2, 14):
        assert isinstance(uno.pins[i], GPIOPin)

    for j in SBArduinoBoard.AnaloguePin:
        assert isinstance(uno.pins[j], GPIOPin)


def test_pin_mutability() -> None:
    """
    Test the mutability of GPIOPins.

    Ensures that GPIOPin objects cannot be lost.
    """
    uno = SBArduinoBoard("SERIAL0", MockSBArduinoBackend())

    with pytest.raises(TypeError):
        uno.pins[2] = True  # type: ignore


def test_uno_make_safe() -> None:
    """Test the make_safe method of the Uno."""
    uno = SBArduinoBoard("SERIAL0", MockSBArduinoBackend())
    uno.make_safe()


def test_uno_supported_components() -> None:
    """Test that the Uno supports the required components."""
    assert {
        GPIOPin,
        LED,
        UltrasoundSensor,
    }.issubset(SBArduinoBoard.supported_components())


def test_uno_ultrasound_sensors() -> None:
    """Test the ultrasound sensors of the arduino."""
    uno = SBArduinoBoard("SERIAL0", MockSBArduinoBackend())
    sensor = uno.ultrasound_sensors[3, 4]
    assert isinstance(sensor, UltrasoundSensor)
    assert sensor._gpio_trigger._identifier == 3
    assert sensor._gpio_echo._identifier == 4
