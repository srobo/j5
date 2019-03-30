"""Tests for the base backend classes."""

from typing import List, Optional

import pytest

from j5.backends import Backend, Environment
from j5.boards import Board


class MockBoard(Board):
    """A test board."""

    @property
    def name(self) -> str:
        """The name of the board."""
        return "Test Board"

    @property
    def serial(self) -> str:
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
    def supported_components() -> List[Type["Component"]]:
        """List the types of component supported by this Board."""
        return []


class Mock2Board(Board):
    """A test board."""

    @property
    def name(self) -> str:
        """The name of the board."""
        return "Test Board 2"

    @property
    def serial(self) -> str:
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
    def supported_components() -> List[Type["Component"]]:
        """List the types of component supported by this Board."""
        return []


MockEnvironment = Environment("TestBackendGroup")


class MockBackend(Backend):
    """A test backend."""

    environment = MockEnvironment
    board = MockBoard

    @classmethod
    def discover(cls) -> List[Board]:
        """Discover boards available on this backend."""
        return []

    def get_firmware_version(self) -> Optional[str]:
        """Get the firmware version of the board."""
        return None


def test_backend_instantiation() -> None:
    """Test that we can instantiate a backend."""
    MockBackend()


def test_environment_supported_boards() -> None:
    """Test that we can get the supported boards for a environment."""
    environment = MockEnvironment
    assert type(environment.supported_boards) == list
    assert len(environment.supported_boards) == 1


def test_environment_board_backend_mapping() -> None:
    """Test that the board_backend_mapping works."""
    environment = MockEnvironment
    assert type(environment.board_backend_mapping) == dict
    assert len(environment.supported_boards) == 1
    assert environment.board_backend_mapping[MockBoard] == MockBackend


def test_environment_board_get_backend() -> None:
    """Test that we can get the backend of a board."""
    environment = MockEnvironment
    assert issubclass(environment.get_backend(MockBoard), MockBackend)


def test_environment_board_get_backend_unknown() -> None:
    """Test that we can't get the backend of an unknown board."""
    environment = MockEnvironment
    with pytest.raises(NotImplementedError):
        assert environment.get_backend(Mock2Board)
