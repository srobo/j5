"""Utility classes for testing."""
from typing import Optional, Set, Type

from j5.backends import Backend
from j5.boards import Board
from j5.components import Component


class MockBoard(Board):
    """A testing board with little to no functionality."""

    def __init__(self, serial: str):
        self._serial = serial
        self._safe = False

    @property
    def name(self) -> str:
        """Get the name of this board."""
        return "Testing Board"

    @property
    def serial_number(self) -> str:
        """Get the serial number of this board."""
        return self._serial

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of this board."""
        return None

    def make_safe(self) -> None:
        """Make this board safe."""
        self._safe = True

    @staticmethod
    def supported_components() -> Set[Type[Component]]:
        """List the types of component supported by this Board."""
        return set()


class MockBoardWithConstructor(MockBoard):
    """A testing board with a constructor."""

    def __init__(self, test_param: str, another_param: str,
                 one_that_defaults: bool = True) -> None:
        self.test_param = test_param
        self.another_param = another_param
        self.one_that_defaults = one_that_defaults


class NoBoardMockBackend(Backend):
    """This backend never finds any testing boards."""

    board = MockBoard

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return None

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover boards available on this backend."""
        return set()


class OneBoardMockBackend(Backend):
    """This backend finds exactly one."""

    board = MockBoard

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return None

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover boards available on this backend."""
        return {MockBoard("TESTSERIAL1")}


class TwoBoardsMockBackend(Backend):
    """This backend finds exactly two."""

    board = MockBoard

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return None

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover boards available on this backend."""
        return {MockBoard("TESTSERIAL1"), MockBoard("TESTSERIAL2")}
