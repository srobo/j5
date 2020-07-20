"""Tests for the string command classes."""

import pytest

from j5.components.string_command import (
    StringCommandComponent,
    StringCommandComponentInterface,
)


class MockStringCommandDriver(StringCommandComponentInterface):
    """A testing driver for the string command component.."""

    def execute_string_command(self, command: str) -> str:
        """Execute a string command."""
        return command[::-1]  # reverse the string


def test_string_command_interface_implementation() -> None:
    """Test that we can implement the interface."""
    MockStringCommandDriver()


def test_string_command_interface_class() -> None:
    """Test that the interface class is correct."""
    assert StringCommandComponent.interface_class() is StringCommandComponentInterface


def test_string_command_instantiation() -> None:
    """Test that we can instantiate the component."""
    StringCommandComponent(0, MockStringCommandDriver())


def test_string_command_identifier() -> None:
    """Test that we can get the identifer of the component."""
    scc = StringCommandComponent(0, MockStringCommandDriver())
    assert scc.identifier == 0


def test_string_command_execute_command() -> None:
    """Test that we can execute a command."""
    scc = StringCommandComponent(0, MockStringCommandDriver())

    assert scc.execute("foo") == "oof"

    with pytest.raises(ValueError):
        scc.execute("")

    with pytest.raises(ValueError):
        scc.execute(9)  # type: ignore


def test_string_command_callable() -> None:
    """Test that we can execute a command using the callable."""
    scc = StringCommandComponent(0, MockStringCommandDriver())

    assert scc("foo") == "oof"

    with pytest.raises(ValueError):
        scc("")

    with pytest.raises(ValueError):
        scc(9)  # type: ignore
