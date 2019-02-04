"""Tests for the Buzzer Classes."""
from j5.backends import Backend
from j5.boards import Board
from j5.components.buzzer import Buzzer, BuzzerInterface


class TestingBuzzerDriver(BuzzerInterface):
    """A testing driver for the buzzer."""

    def buzz(self, board: Board, identifier: int, length: int,
             frequency: int = None, note: str = None) -> None:
        """Set the state of an buzzer."""
        pass


class TestingBuzzerBoard(Board):
    """A testing board for the buzzer."""

    @property
    def name(self) -> str:
        """The name of this board."""
        return "Testing Buzzer Board"

    @property
    def serial(self) -> str:
        """The serial number of this board."""
        return "SERIAL"

    @property
    def components(self):
        """List the components that this Board supports."""
        return [Buzzer]

    @staticmethod
    def discover(backend: Backend):
        """Detect all of the boards on a given backend."""
        return []


def test_buzzer_interface_implementation():
    """Test that we can implement the BuzzerInterface."""
    TestingBuzzerDriver()


def test_buzzer_instantiation():
    """Test that we can instantiate an buzzer."""
    Buzzer(0, TestingBuzzerBoard(), TestingBuzzerDriver())
