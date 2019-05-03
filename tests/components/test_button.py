"""Tests for the Button Classes."""
from time import sleep, time

from j5.components.button import Button, ButtonInterface


class MockButtonDriver(ButtonInterface):
    """A testing driver for the button component."""

    def __init__(self) -> None:
        self.state = False

    def set_button_state(self, new_state: bool) -> None:
        """Set the button state for testing purposes."""
        self.state = new_state

    def get_button_state(self, identifier: int) -> bool:
        """Get the state of the button."""
        return self.state

    def wait_until_button_pressed(self, identifier: int) -> None:
        """Wait until the button was pressed."""
        sleep(0.2)  # The mock driver always presses the button after 0.2s


def test_button_interface_implementation() -> None:
    """Test that we can implement the button interface."""
    MockButtonDriver()


def test_button_instantiation() -> None:
    """Test that we can instantiate a button."""
    Button(0, MockButtonDriver())


def test_button_interface_class() -> None:
    """Test that the Button Interface class is a ButtonInterface."""
    assert Button.interface_class() is ButtonInterface


def test_button_identifier() -> None:
    """Test the identifier attribute of the component."""
    component = Button(0, MockButtonDriver())
    assert component.identifier == 0


def test_button_state() -> None:
    """Test that we can get the state of the button."""
    driver = MockButtonDriver()
    button = Button(0, driver)

    assert button.is_pressed is False
    driver.set_button_state(True)
    assert button.is_pressed is True


def test_button_wait_until_pressed() -> None:
    """Test that the button takes at least 0.2 secs to be pressed."""
    button = Button(0, MockButtonDriver())
    start_time = time()
    button.wait_until_pressed()
    end_time = time()
    time_taken = end_time - start_time

    assert time_taken > 0.2
    assert time_taken < 2
