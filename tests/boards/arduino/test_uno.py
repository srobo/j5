"""Tests for the Arduino Uno and related classes."""

from typing import TYPE_CHECKING, Optional, Set

from j5.backends import Backend, Environment
from j5.boards.arduino import AnaloguePin, ArduinoUnoBoard
from j5.components import GPIOPin, GPIOPinInterface, GPIOPinMode, LEDInterface

if TYPE_CHECKING:
    from j5.boards import Board  # noqa


MockEnvironment = Environment("MockEnvironment")


class MockArduinoUnoBackend(
    GPIOPinInterface,
    LEDInterface,
    Backend,
):
    """Mock Backend for testing the Arduino Uno."""

    environment = MockEnvironment
    board = ArduinoUnoBoard

    def set_gpio_pin_mode(self, identifier: int, pin_mode: GPIOPinMode) -> None:
        """Set the GPIO pin mode."""
        pass

    def get_gpio_pin_mode(self, identifier: int) -> GPIOPinMode:
        """Get the GPIO pin mode."""
        return GPIOPinMode.DIGITAL_OUTPUT

    def write_gpio_pin_digital_state(self, identifier: int, state: bool) -> None:
        """Set the GPIO pin digital state."""
        pass

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
        pass

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
    ArduinoUnoBoard("SERIAL0", MockArduinoUnoBackend())


def test_uno_discover() -> None:
    """Test that we can discover Unos."""
    assert MockArduinoUnoBackend.discover() == set()


def test_uno_name() -> None:
    """Test the name attribute of the Uno."""
    uno = ArduinoUnoBoard("SERIAL0", MockArduinoUnoBackend())

    assert uno.name == "Arduino Uno"


def test_uno_serial() -> None:
    """Test the serial attribute of the Uno."""
    uno = ArduinoUnoBoard("SERIAL0", MockArduinoUnoBackend())

    assert uno.serial == "SERIAL0"


def test_uno_firmware_version() -> None:
    """Test the firmware_version attribute of the Uno."""
    uno = ArduinoUnoBoard("SERIAL0", MockArduinoUnoBackend())

    assert uno.firmware_version is None


def test_uno_make_safe() -> None:
    """Test the make_safe method of the Uno."""
    uno = ArduinoUnoBoard("SERIAL0", MockArduinoUnoBackend())
    uno.make_safe()


def test_uno_pins() -> None:
    """Test the pins of the Uno."""
    uno = ArduinoUnoBoard("SERIAL0", MockArduinoUnoBackend())

    assert len(uno.pins) == 12 + 6

    for i in range(2, 14):
        assert type(uno.pins[i]) is GPIOPin

    for j in AnaloguePin:
        assert type(uno.pins[j]) is GPIOPin
