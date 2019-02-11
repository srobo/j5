"""Tests for the Piezo Classes."""
from j5.backends import Backend
from j5.boards import Board
from j5.components.piezo import Piezo, PiezoInterface


class MockPiezoDriver(PiezoInterface):
    """A testing driver for the piezo."""

    def buzz(self, board: Board, identifier: int, length: int,
             frequency: int = None, note: str = None) -> None:
        """Set the state of an piezo."""
        pass


class MockPiezoBoard(Board):
    """A testing board for the piezo."""

    @property
    def name(self) -> str:
        """The name of this board."""
        return "Mock Piezo Board"

    @property
    def serial(self) -> str:
        """The serial number of this board."""
        return "SERIAL"

    @property
    def supported_components(self):
        """List the components that this Board supports."""
        return [Piezo]

    def make_safe(self):
        """Make this board safe."""
        pass

    @staticmethod
    def discover(backend: Backend):
        """Detect all of the boards on a given backend."""
        return []


def test_piezo_interface_implementation():
    """Test that we can implement the PiezoInterface."""
    MockPiezoDriver()


def test_piezo_instantiation():
    """Test that we can instantiate an piezo."""
    Piezo(0, MockPiezoBoard(), MockPiezoDriver())
