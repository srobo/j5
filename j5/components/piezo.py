"""Classes for the Piezo support."""

from abc import ABCMeta, abstractmethod

from j5.boards import Board
from j5.components import Component


class PiezoInterface(metaclass=ABCMeta):
    """An interface containing the methods required to control an piezo."""

    @abstractmethod
    def buzz(self, board: Board, identifier: int, length: int,
             frequency: int = None, note: str = None) -> None:
        """Set the state of an piezo."""
        raise NotImplementedError  # pragma: no cover


class Piezo(Component):
    """A standard piezo."""

    def __init__(self, identifier: int, board: Board, backend: PiezoInterface) -> None:
        self._board = board
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class():
        """Get the interface class that is required to use this component."""
        return PiezoInterface
