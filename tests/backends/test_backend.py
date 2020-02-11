"""Tests for the base backend classes."""

from typing import TYPE_CHECKING, Optional, Set, Type

import pytest

from j5.backends import Backend
from j5.boards import Board
from j5.components import LED

from .utils import MockBackend

if TYPE_CHECKING:
    from j5.components import Component  # noqa


def test_backend_instantiation() -> None:
    """Test that we can instantiate a backend."""
    MockBackend()


def test_backend_has_required_interface() -> None:
    """Test that the backend has to have the required interfaces."""
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
            board = LEDMockBoard

            @classmethod
            def discover(cls) -> Set['Board']:
                return set()

            @property
            def firmware_version(self) -> Optional[str]:
                return None
