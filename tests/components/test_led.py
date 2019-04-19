"""Tests for the LED Classes."""
from j5.components.led import LED, LEDInterface


class MockLEDDriver(LEDInterface):
    """A testing driver for the led."""

    def set_led_state(self, identifier: int, state: bool) -> None:
        """Set the state of an led."""
        pass

    def get_led_state(self, identifier: int) -> bool:
        """Get the state of an LED."""
        return True


def test_led_interface_implementation() -> None:
    """Test that we can implement the LEDInterface."""
    MockLEDDriver()


def test_led_instantiation() -> None:
    """Test that we can instantiate an LED."""
    LED(0, MockLEDDriver())


def test_led_state() -> None:
    """Test the state property of an LED."""
    led = LED(0, MockLEDDriver())

    led.state = True
    assert led.state
