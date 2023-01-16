"""Tests for the ConsoleEnvironment and Console helper."""

from j5.backends.console import Console


def test_console_instantiation() -> None:
    """Test that we can create a console."""
    console = Console("MockConsole")

    assert type(console) is Console
    assert console._descriptor == "MockConsole"


def test_console_info() -> None:
    """Test that the console can output information."""

    class MockPrintConsole(Console):
        """Define a testing print function."""

        def _print(self, text: str) -> None:
            """Mock printing function."""
            assert text == "TestBoard: Test the console info"

    console = MockPrintConsole("TestBoard")

    console.info("Test the console info")


def test_console_read() -> None:
    """Test that we can read from the console."""

    class MockInputConsole(Console):
        """Define a testing input function."""

        def _input(self, prompt: str) -> str:
            """Mock some input."""
            return str(reversed(prompt))

    console = MockInputConsole("TestBoard")

    assert str(console.read("Enter Test Input")) == str(reversed("Enter Test Input"))


def test_console_read_none_type() -> None:
    """Test that we can read None from console, i.e any input."""

    class ConsoleNone(Console):
        """Define a testing input function."""

        def _input(self, prompt: str) -> str:
            """Mock some input."""
            return "string"

    console = ConsoleNone("TestBoard")
    assert console.read("Enter test input", None) is None


def test_console_read_bad_type() -> None:
    """Test that the console emits an error if it cannot cast to the desired type."""
    class MockConsoleWithState(Console):
        """A mock console with state."""

        def __init__(self, descriptor: str) -> None:
            super().__init__(descriptor)
            self.bad_attempt_count = 0

        def _input(self, prompt: str) -> str:  # noqa: A003
            """Mock some input."""
            if self.bad_attempt_count == 0:
                self.bad_attempt_count += 1
                return "Not an int"
            return "6"

        def _print(self, text: str) -> None:  # noqa: A003,T002
            """Mock printing function."""
            if self.bad_attempt_count == 0:
                assert text == "TestConsole: Unable to construct a int from 'Not an int'"

    console = MockConsoleWithState("TestConsole")

    assert console.read("I want an int", int) == 6


def test_console_handle_boolean_correctly() -> None:
    """Test that the console handles bools correctly."""
    class MockConsoleBoolean(Console):
        """A mock console with state."""

        true_cases = ["yes", "YES", "YeS", "True"]
        false_cases = ["no", "NO", "No", "False"]
        extra_cases = ["bees", "foo", "0", "True"]

        def __init__(self, descriptor: str) -> None:
            super().__init__(descriptor)
            self._pos = 0
            self.cases = self.true_cases + self.false_cases + self.extra_cases

        def _input(self, prompt: str) -> str:  # noqa: A003
            """Mock some input."""
            val = self.cases[self._pos]
            self._pos += 1
            return val

        def _print(self, text: str) -> None:  # noqa: A003,T002
            """Mock printing function."""
            if self._pos in [8, 9, 10, 11]:
                assert text == f"TestConsole: Unable to construct a bool " \
                    f"from {self.cases[self._pos - 1]!r}"
            else:
                raise AssertionError()

        @property
        def is_finished(self) -> bool:
            """Check if all of the cases have been consumed."""
            return self._pos == len(self.cases)

    console = MockConsoleBoolean("TestConsole")

    for _ in MockConsoleBoolean.true_cases:
        val = console.read("I want an bool", bool, check_stdin=False)
        assert isinstance(val, bool)
        assert val

    for _ in MockConsoleBoolean.false_cases:
        val = console.read("I want an bool", bool, check_stdin=False)
        assert isinstance(val, bool)
        assert not val

    # Test if false inputs are skipped.
    val = console.read("I want an bool", bool, check_stdin=False)
    assert isinstance(val, bool)
    assert val

    assert console.is_finished
