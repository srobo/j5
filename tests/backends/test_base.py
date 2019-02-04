"""Tests for the base backend classes."""

import pytest

from j5.backends import Backend, Environment
from j5.boards import Board


class MockBoard(Board):
    """A test board."""

    def __init__(self):
        self.setup()

    @property
    def name(self) -> str:
        """The name of the board."""
        return "Test Board"

    @property
    def serial(self) -> str:
        """The serial number of the board."""
        return "TEST"

    def make_safe(self):
        """Make this board safe."""
        pass

    @staticmethod
    def supported_components():
        """List the types of component supported by this Board."""
        return []

    @staticmethod
    def discover(backend: Backend):
        """Get all boards of this type."""
        return []


class Mock2Board(Board):
    """A test board."""

    def __init__(self):
        self.setup()

    @property
    def name(self) -> str:
        """The name of the board."""
        return "Test Board 2"

    @property
    def serial(self) -> str:
        """The serial number of the board."""
        return "TEST2"

    def make_safe(self):
        """Make this board safe."""
        pass

    @staticmethod
    def supported_components():
        """List the types of component supported by this Board."""
        return []

    @staticmethod
    def discover(backend: Backend):
        """Get all boards of this type."""
        return []


MockEnvironment = Environment("TestBackendGroup")


class MockBackend(Backend):
    """A test backend."""

    environment = MockEnvironment
    board = MockBoard


def test_backend_instantiation():
    """Test that we can instantiate a backend."""
    MockBackend()


def test_environment_supported_boards():
    """Test that we can get the supported boards for a environment."""
    environment = MockEnvironment
    assert type(environment.supported_boards) == list
    assert len(environment.supported_boards) == 1


def test_environment_board_backend_mapping():
    """Test that the board_backend_mapping works."""
    environment = MockEnvironment
    assert type(environment.board_backend_mapping) == dict
    assert len(environment.supported_boards) == 1
    assert environment.board_backend_mapping[MockBoard] == MockBackend


def test_environment_board_get_backend():
    """Test that we can get the backend of a board."""
    environment = MockEnvironment
    assert isinstance(environment.get_backend(MockBoard), MockBackend)


def test_environment_board_get_backend_unknown():
    """Test that we can't get the backend of an unknown board."""
    environment = MockEnvironment
    with pytest.raises(NotImplementedError):
        assert environment.get_backend(Mock2Board)
