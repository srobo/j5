"""Classes for Button."""

from abc import ABCMeta, abstractmethod

from j5.boards import Board
from j5.components import Component


class ButtonInterface(metaclass=ABCMeta):
    """An interface containing the methods required for a button."""

    @abstractmethod
    def get_button_state(self, board: Board, identifier: int) -> bool:
        """Set the state of a button."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def wait_until_button_pressed(self, board: Board, identifier: int) -> bool:
        """Halt the program until this button is pushed."""
        raise NotImplementedError  # pragma: no cover


class Button(Component):
    """A button."""

    def __init__(self, identifier: int, board: Board, backend: ButtonInterface) -> None:
        self._board = board
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class():
        """Get the interface class that is required to use this component."""
        return ButtonInterface

    @property
    def is_pressed(self) -> bool:
        """Get the current pushed state of the button."""
        return self._backend.get_button_state(self._board, self._identifier)

    def wait_until_pressed(self):
        """Halt the program until this button is pushed."""
        self._backend.wait_until_button_pressed(self._board, self._identifier)
