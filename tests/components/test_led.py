"""Tests for the LED Classes."""
from j5.backends import Backend
from j5.boards import Board
from j5.components.led import LED, LEDInterface


class TestingLEDDriver(LEDInterface):
    """A testing driver for the led."""

    def set_led_state(self, board: Board, identifier: int, state: bool) -> None:
        """Set the state of an led."""
        pass

    def get_led_state(self, board: Board, identifier: int) -> bool:
        """Get the state of an LED."""
        return True


class TestingLEDBoard(Board):
    """A testing board for the led."""

    def __init__(self):
        self.setup()

    @property
    def name(self) -> str:
        """The name of this board."""
        return "Testing LED Board"

    @property
    def serial(self) -> str:
        """The serial number of this board."""
        return "SERIAL"

    @property
    def components(self):
        """List the components that this Board supports."""
        return [LED]

    def make_safe(self):
        """Make this board safe."""
        pass

    @staticmethod
    def discover(backend: Backend):
        """Detect all of the boards on a given backend."""
        return []


def test_led_interface_implementation():
    """Test that we can implement the LEDInterface."""
    TestingLEDDriver()


def test_led_instantiation():
    """Test that we can instantiate an LED."""
    LED(0, TestingLEDBoard(), TestingLEDDriver())


def test_led_state():
    """Test the state property of an LED."""
    led = LED(0, TestingLEDBoard(), TestingLEDDriver())

    led.state = True
    assert led.state
