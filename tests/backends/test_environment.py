"""Test environment and related."""

from typing import Optional, Set

import pytest

from j5.backends import Backend, Environment
from j5.boards import Board

from .utils import Mock2Board, MockBackend, MockBoard


def test_environment_supported_boards() -> None:
    """Test that we can get the supported boards for a environment."""
    environment = Environment("MockEnv")
    environment.register_backend(MockBackend)
    assert type(environment.supported_boards) is set
    assert len(environment.supported_boards) == 1


def test_environment_board_backend_mapping() -> None:
    """Test that the board_backend_mapping works."""
    environment = Environment("MockEnv")
    environment.register_backend(MockBackend)
    assert type(environment.board_backend_mapping) == dict
    assert len(environment.supported_boards) == 1
    assert environment.board_backend_mapping[MockBoard] == MockBackend


def test_environment_board_get_backend() -> None:
    """Test that we can get the backend of a board."""
    environment = Environment("MockEnv")
    environment.register_backend(MockBackend)
    assert issubclass(environment.get_backend(MockBoard), MockBackend)


def test_environment_board_get_backend_unknown() -> None:
    """Test that we can't get the backend of an unknown board."""
    environment = Environment("MockEnv")
    environment.register_backend(MockBackend)
    with pytest.raises(NotImplementedError):
        assert environment.get_backend(Mock2Board)


def test_environment_get_board_group() -> None:
    """Test that we can create a boardgroup from an environment."""
    env = Environment("TestEnv")
    env.register_backend(MockBackend)

    bg = env.get_board_group(MockBoard)

    assert bg.backend_class is MockBackend


def test_environment_merge() -> None:
    """Test that we can merge environments."""
    env1 = Environment("Env1")
    env2 = Environment("Env2")

    assert len(env1.supported_boards) == 0
    assert len(env2.supported_boards) == 0

    env1.merge(env2)
    assert len(env1.supported_boards) == 0
    assert len(env2.supported_boards) == 0

    env2.register_backend(MockBackend)
    assert len(env2.supported_boards) == 1

    env1.merge(env2)
    assert len(env1.supported_boards) == 1
    assert len(env2.supported_boards) == 1


def test_environment_merge_duplicate() -> None:
    """Test that the correct exception is thrown if duplicate entries exist."""
    env1 = Environment("Env1")
    env2 = Environment("Env2")

    env1.register_backend(MockBackend)
    env2.register_backend(MockBackend)

    with pytest.raises(RuntimeError) as e:
        env1.merge(env2)
    assert e is not None
    assert str(e.value) == \
        "Attempted to merge two Environments that both contain: MockBoard"


def test_environment_check_multiple_backends_same_env() -> None:
    """Test that we can't define two backends for the same board/environment combo."""
    test_environment = Environment("test_environment")

    class BackendOne(Backend):
        board = MockBoard

        @classmethod
        def discover(cls) -> Set[Board]:
            return set()

        @property
        def firmware_version(self) -> Optional[str]:
            return None

    class BackendTwo(Backend):

        board = MockBoard

        @classmethod
        def discover(cls) -> Set[Board]:
            return set()

        @property
        def firmware_version(self) -> Optional[str]:
            return None

    test_environment.register_backend(BackendOne)

    with pytest.raises(RuntimeError):
        test_environment.register_backend(BackendTwo)
