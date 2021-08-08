"""Classes for Button."""

from abc import abstractmethod
from typing import Type

from j5.components.component import Component, Interface


class ButtonInterface(Interface):
    """An interface containing the methods required for a button."""

    @abstractmethod
    def get_button_state(self, identifier: int) -> bool:
        """
        Get the state of a button.

        :param identifier: Button identifier to fetch state of.
        :returns: state of the button.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def wait_until_button_pressed(self, identifier: int) -> None:
        """
        Halt the program until this button is pushed.

        :param identifier: Button identifier to wait for.
        """
        raise NotImplementedError  # pragma: no cover


class Button(Component):
    """A button."""

    def __init__(self, identifier: int, backend: ButtonInterface) -> None:
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class() -> Type[ButtonInterface]:
        """
        Get the interface class that is required to use this component.

        :returns: interface class.
        """
        return ButtonInterface

    @property
    def identifier(self) -> int:
        """
        An integer to identify the component on a board.

        :returns: component identifier.
        """
        return self._identifier

    @property
    def is_pressed(self) -> bool:
        """
        Get the current pushed state of the button.

        :returns: current pushed state of the button.
        """
        return self._backend.get_button_state(self._identifier)

    def wait_until_pressed(self) -> None:
        """Halt the program until this button is pushed."""
        self._backend.wait_until_button_pressed(self._identifier)
