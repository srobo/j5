"""Tests for the LED Classes."""
from typing import List, Optional, Type

from j5.boards import Board
from j5.components.led import LED, LEDInterface


class MockLEDDriver(LEDInterface):
    """A testing driver for the led."""

    def set_led_state(self, identifier: int, state: bool) -> None:
        """Set the state of an led."""
        pass

    def get_led_state(self, identifier: int) -> bool:
        """Get the state of an LED."""
        return True


class MockLEDBoard(Board):
    """A testing board for the led."""

    def __init__(self) -> None:
        pass

    @property
    def name(self) -> str:
        """The name of this board."""
        return "Testing LED Board"

    @property
    def serial(self) -> str:
        """The serial number of this board."""
        return "SERIAL"

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of this board."""
        return None

    @staticmethod
    def supported_components() -> List[Type['Component']]:
        """List the types of component that this Board supports."""
        return [LED]

    def make_safe(self) -> None:
        """Make this board safe."""
        pass


def test_led_interface_implementation() -> None:
    """Test that we can implement the LEDInterface."""
    MockLEDDriver()


def test_led_instantiation() -> None:
    """Test that we can instantiate an LED."""
    LED(0, MockLEDBoard(), MockLEDDriver())


def test_led_state() -> None:
    """Test the state property of an LED."""
    led = LED(0, MockLEDBoard(), MockLEDDriver())

    led.state = True
    assert led.state
