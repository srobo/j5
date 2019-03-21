"""Tests for the ConsoleEnvironment and Console helper."""

from j5.backends import Environment
from j5.backends.console import Console, ConsoleEnvironment


def test_hardware_environment():
    """Test that the Hardware Environment works."""
    assert type(ConsoleEnvironment) is Environment

    assert ConsoleEnvironment.name == "ConsoleEnvironment"


def test_console_instantiation():
    """Test that we can create a console."""
    console = Console("TestConsole")

    assert type(console) is Console
    assert console._descriptor == "TestConsole"
    assert console._print is print
    assert console._input is input


def test_console_info():
    """Test that the console can output information."""
    # Define a testing print function
    def mock_print(text: str):
        """Mock printing function."""
        assert text == "TestBoard: Test the console info"

    console = Console("TestBoard", print_function=mock_print)

    console.info("Test the console info")


def test_console_read():
    """Test that we can read from the console."""
    # Define a testing input function
    def mock_input(prompt: str):
        """Mock some input."""
        return reversed(prompt)

    console = Console("TestBoard", input_function=mock_input)

    assert str(console.read("Enter Test Input")) == str(reversed("Enter Test Input"))
