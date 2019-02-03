"""Tests for the base backend classes."""

import pytest

from j5.backends import Backend, Environment
from j5.boards import Board


class TestBoard(Board):
    """A test board."""

    @property
    def name(self) -> str:
        """The name of the board."""
        return "Test Board"

    @property
    def serial(self) -> str:
        """The serial number of the board."""
        return "TEST"

    @staticmethod
    def components():
        """List the components on this Board."""
        return []

    @staticmethod
    def discover(backend: Backend):
        """Get all boards of this type."""
        return []


class Test2Board(Board):
    """A test board."""

    @property
    def name(self) -> str:
        """The name of the board."""
        return "Test Board 2"

    @property
    def serial(self) -> str:
        """The serial number of the board."""
        return "TEST2"

    @staticmethod
    def components():
        """List the components on this Board."""
        return []

    @staticmethod
    def discover(backend: Backend):
        """Get all boards of this type."""
        return []


TestEnvironment = Environment("TestBackendGroup")


class TestBackend(Backend):
    """A test backend."""

    environment = TestEnvironment
    board = TestBoard


def test_backend_instantiation():
    """Test that we can instantiate a backend."""
    TestBackend()


def test_environment_supported_boards():
    """Test that we can get the supported boards for a environment."""
    environment = TestEnvironment
    assert type(environment.supported_boards) == list
    assert len(environment.supported_boards) == 1


def test_environment_board_backend_mapping():
    """Test that the board_backend_mapping works."""
    environment = TestEnvironment
    assert type(environment.board_backend_mapping) == dict
    assert len(environment.supported_boards) == 1
    assert environment.board_backend_mapping[TestBoard] == TestBackend


def test_environment_board_get_backend():
    """Test that we can get the backend of a board."""
    environment = TestEnvironment
    assert isinstance(environment.get_backend(TestBoard), TestBackend)


def test_environment_board_get_backend_unknown():
    """Test that we can't get the backend of an unknown board."""
    environment = TestEnvironment
    with pytest.raises(NotImplementedError):
        assert environment.get_backend(Test2Board)
