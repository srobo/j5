"""Tests for the base backend classes."""

from typing import TYPE_CHECKING, Optional, Set, Type

import pytest

from j5.backends import Backend, Environment
from j5.boards import Board
from j5.components import LED

if TYPE_CHECKING:
    from j5.components import Component  # noqa


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
    def supported_components() -> Set[Type["Component"]]:
        """List the types of component supported by this Board."""
        return set()


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
    def supported_components() -> Set[Type["Component"]]:
        """List the types of component supported by this Board."""
        return set()


MockEnvironment = Environment("TestBackendGroup")


class MockBackend(Backend):
    """A test backend."""

    environment = MockEnvironment
    board = MockBoard

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover boards available on this backend."""
        return set()

    def get_firmware_version(self) -> Optional[str]:
        """Get the firmware version of the board."""
        return None


def test_backend_instantiation() -> None:
    """Test that we can instantiate a backend."""
    MockBackend()


def test_environment_supported_boards() -> None:
    """Test that we can get the supported boards for a environment."""
    environment = MockEnvironment
    assert type(environment.supported_boards) is set
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


def test_backend_check_has_environment() -> None:
    """Test that an error is thrown if a backend is defined without an environment."""
    with pytest.raises(ValueError):
        class NoEnvironmentBackend(Backend):
            """I have no environment."""

            board = MockBoard

            @classmethod
            def discover(cls) -> Set['Board']:
                return set()

            def get_firmware_version(self) -> Optional[str]:
                return None


def test_backend_check_multiple_backends_same_env() -> None:
    """Test that we can't define two backends for the same board/environment combo."""
    test_environment = Environment("test_environment")

    with pytest.raises(RuntimeError):
        class BackendOne(Backend):
            """I have no environment."""

            board = MockBoard
            environment = test_environment

            @classmethod
            def discover(cls) -> Set['Board']:
                return set()

            def get_firmware_version(self) -> Optional[str]:
                return None

        class BackendTwo(Backend):
            """I have no environment."""

            board = MockBoard
            environment = test_environment

            @classmethod
            def discover(cls) -> Set['Board']:
                return set()

            def get_firmware_version(self) -> Optional[str]:
                return None


def test_backend_has_required_interface() -> None:
    """Test that the backend has to have the required interfaces."""
    test_environment = Environment("test_environment")

    class LEDMockBoard(Board):
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
        def supported_components() -> Set[Type["Component"]]:
            """List the types of component supported by this Board."""
            return {LED}

    with pytest.raises(TypeError):
        class BackendTwo(Backend):
            """I have no environment."""

            board = LEDMockBoard
            environment = test_environment

            @classmethod
            def discover(cls) -> Set['Board']:
                return set()

            def get_firmware_version(self) -> Optional[str]:
                return None
