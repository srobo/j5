"""Tests for the ConsoleEnvironment and Console helper."""

from j5.backends import Environment
from j5.backends.console import Console, ConsoleEnvironment


def test_console_environment() -> None:
    """Test that the Console Environment works."""
    assert type(ConsoleEnvironment) is Environment

    assert ConsoleEnvironment.name == "ConsoleEnvironment"


def test_console_instantiation() -> None:
    """Test that we can create a console."""
    console = Console("MockConsole")

    assert type(console) is Console
    assert console._descriptor == "MockConsole"
    assert console._print is print
    assert console._input is input


def test_console_info() -> None:
    """Test that the console can output information."""
    # Define a testing print function
    def mock_print(text: str) -> None:
        """Mock printing function."""
        assert text == "TestBoard: Test the console info"

    console = Console("TestBoard", print_function=mock_print)

    console.info("Test the console info")


def test_console_read() -> None:
    """Test that we can read from the console."""
    # Define a testing input function
    def mock_input(prompt: str) -> str:
        """Mock some input."""
        return str(reversed(prompt))

    console = Console("TestBoard", input_function=mock_input)

    assert str(console.read("Enter Test Input")) == str(reversed("Enter Test Input"))


def test_console_read_none_type() -> None:
    """Test that we can read None from console, i.e any input."""
    # Define a testing input function
    def mock_input(prompt: str) -> str:
        """Mock some input."""
        return "string"

    console = Console("TestBoard", input_function=mock_input)
    assert console.read("Enter test input", None) is None


BAD_ATTEMPT_COUNT = 0


def test_console_read_bad_type() -> None:
    """Test that the console emits an error if it cannot cast to the desired type."""
    def mock_input(prompt: str) -> str:
        """Mock some input."""
        global BAD_ATTEMPT_COUNT
        if BAD_ATTEMPT_COUNT == 0:
            BAD_ATTEMPT_COUNT += 1
            return "Not an int"
        return "6"

    def mock_print(text: str) -> None:
        """Mock printing function."""
        global BAD_ATTEMPT_COUNT
        if BAD_ATTEMPT_COUNT == 0:
            assert text == "TestConsole: Unable to construct a int from 'Not an int'"

    console = Console(
        "TestConsole",
        print_function=mock_print,
        input_function=mock_input,
    )

    assert console.read("I want an int", int) == 6
