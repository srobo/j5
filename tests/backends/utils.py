"""Utility classes for testing environments and backends."""

from typing import Optional, Set, Type

from j5.backends import Backend
from j5.boards import Board
from j5.components import Component


class MockBoard(Board):
    """A test board."""

    @property
    def name(self) -> str:
        """The name of the board."""
        return "Test Board"

    @property
    def serial_number(self) -> str:
        """The serial number of the board."""
        return "TEST"

    def make_safe(self) -> None:
        """Make this board safe."""
        pass

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of this board."""
        return None

    @staticmethod
    def supported_components() -> Set[Type[Component]]:
        """List the types of component supported by this Board."""
        return set()


class Mock2Board(Board):
    """A test board."""

    @property
    def name(self) -> str:
        """The name of the board."""
        return "Test Board 2"

    @property
    def serial_number(self) -> str:
        """The serial number of the board."""
        return "TEST2"

    def make_safe(self) -> None:
        """Make this board safe."""
        pass

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of this board."""
        return None

    @staticmethod
    def supported_components() -> Set[Type[Component]]:
        """List the types of component supported by this Board."""
        return set()


class MockBackend(Backend):
    """A test backend."""

    board = MockBoard

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover boards available on this backend."""
        return set()

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return None
