"""Classes for the Buzzer support."""

from abc import ABCMeta, abstractmethod

from j5.boards import Board
from j5.components import Component


class BuzzerInterface(metaclass=ABCMeta):
    """An interface containing the methods required to control an buzzer."""

    @abstractmethod
    def buzz(self, board: Board, identifier: int, length: int,
             frequency: int = None, note: str = None) -> None:
        """Set the state of an buzzer."""
        raise NotImplementedError  # pragma: no cover


class Buzzer(Component):
    """A standard buzzer."""

    def __init__(self, identifier: int, board: Board, backend: BuzzerInterface) -> None:
        self._board = board
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class():
        """Get the interface class that is required to use this component."""
        return BuzzerInterface
