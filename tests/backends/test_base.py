"""Tests for the base backend classes."""

from typing import Mapping

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
    def detect_all(backend: Backend):
        """Get all boards of this type."""
        return []


class TestBackend(Backend):
    """A test backend."""

    pass


class TestBackendGroup(BackendGroup):
    """A test backend group."""

    @property
    def supported_boards(self) -> Mapping[Board, Backend]:
        """The supported boards for this backend group."""
        return {TestBoard: TestBackend}  # type: ignore


def test_backend_instantiation():
    """Test that we can instantiate a backend."""
    TestBackend()


def test_backend_group_instantiation():
    """Test that we can instantiate a backend group."""
    TestBackendGroup()


def test_backend_group_supported_boards():
    """Test that we can get the supported boards for a backend group."""
    tbg = TestBackendGroup()
    assert len(tbg.supported_boards) == 1


def test_backend_group_board_get_backend():
    """Test that we can get the backend of a board."""
    tbg = TestBackendGroup()
    assert tbg.get_backend(TestBoard)


def test_backend_group_board_get_backend_unknown():
    """Test that we can't get the backend of an unknown board."""
    tbg = TestBackendGroup()
    with pytest.raises(NotImplementedError):
        assert tbg.get_backend(Test2Board)
