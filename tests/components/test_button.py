"""Tests for the Button Classes."""
from time import sleep, time
from typing import List, Optional, Type

from j5.backends import Backend
from j5.boards import Board
from j5.components import Component
from j5.components.button import Button, ButtonInterface


class MockButtonDriver(ButtonInterface):
    """A testing driver for the button component."""

    def __init__(self):
        self.state = False

    def set_button_state(self, new_state: bool):
        """Set the button state for testing purposes."""
        self.state = new_state

    def get_button_state(self, identifier: int) -> bool:
        """Get the state of the button."""
        return self.state

    def wait_until_button_pressed(self, identifier: int) -> bool:
        """Wait until the button was pressed."""
        sleep(0.2)  # The mock driver always presses the button after 0.2s


class MockButtonBoard(Board):
    """A testing board for the button."""

    @property
    def name(self) -> str:
        """The name of this board."""
        return "Testing Button Board"

    @property
    def serial(self) -> str:
        """The serial number of this board."""
        return "SERIAL"

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of this board."""
        return self._backend.get_firmware_version()

    def make_safe(self):
        """Make this board safe."""
        pass

    @staticmethod
    def supported_components() -> List[Type[Component]]:
        """List the types of component that this Board supports."""
        return [Button]

    @staticmethod
    def discover(backend: Backend) -> List[Board]:
        """Detect all of the boards on a given backend."""
        return []


def test_button_interface_implementation():
    """Test that we can implement the button interface."""
    MockButtonDriver()


def test_button_instantiation():
    """Test that we can instantiate a button."""
    Button(0, MockButtonBoard(), MockButtonDriver())


def test_button_state():
    """Test that we can get the state of the button."""
    driver = MockButtonDriver()
    button = Button(0, MockButtonBoard(), driver)

    assert button.is_pressed is False
    driver.set_button_state(True)
    assert button.is_pressed is True


def test_button_wait_until_pressed():
    """Test that the button takes at least 0.2 secs to be pressed."""
    button = Button(0, MockButtonBoard(), MockButtonDriver())
    start_time = time()
    button.wait_until_pressed()
    end_time = time()
    time_taken = end_time - start_time

    assert time_taken > 0.2
    assert time_taken < 2


def test_button_interface_class():
    """Test that the Button Interface class is a ButtonInterface."""
    assert Button.interface_class() is ButtonInterface
