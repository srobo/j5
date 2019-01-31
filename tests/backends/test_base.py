"""Tests for the base backend classes."""

import pytest

from j5.backends import Backend, BackendGroup
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
    def supported_components():
        """List the components that this Board supports."""
        return []

    @staticmethod
    def detect_all(backend: Backend):
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
    def supported_components():
        """List the components that this Board supports."""
        return []

    @staticmethod
    def detect_all(backend: Backend):
        """Get all boards of this type."""
        return []


TestBackendGroup = BackendGroup("TestBackendGroup")


class TestBackend(Backend):
    """A test backend."""

    group = TestBackendGroup
    board = TestBoard


def test_backend_instantiation():
    """Test that we can instantiate a backend."""
    TestBackend()


def test_backend_group_supported_boards():
    """Test that we can get the supported boards for a backend group."""
    tbg = TestBackendGroup
    assert type(tbg.supported_boards) == list
    assert len(tbg.supported_boards) == 1


def test_backend_group_board_backend_mapping():
    """Test that the board_backend_mapping works."""
    tbg = TestBackendGroup
    assert type(tbg.board_backend_mapping) == dict
    assert len(tbg.supported_boards) == 1
    assert tbg.board_backend_mapping[TestBoard] == TestBackend


def test_backend_group_board_get_backend():
    """Test that we can get the backend of a board."""
    tbg = TestBackendGroup
    assert isinstance(tbg.get_backend(TestBoard), TestBackend)


def test_backend_group_board_get_backend_unknown():
    """Test that we can't get the backend of an unknown board."""
    tbg = TestBackendGroup
    with pytest.raises(NotImplementedError):
        assert tbg.get_backend(Test2Board)
