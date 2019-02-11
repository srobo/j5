"""Classes for Piezo support."""

from abc import ABCMeta, abstractmethod
from datetime import timedelta
from enum import Enum
from typing import TypeVar

from j5.boards import Board
from j5.components import Component


class Note(Enum):
    """An enumerator of frequencies in Hz."""

    C6 = 1046.50
    D6 = 1174.66
    E6 = 1318.51
    F6 = 1396.91
    G6 = 1567.98
    A6 = 1760.00
    B6 = 1975.53
    C7 = 2093.00
    D7 = 2349.32
    E7 = 2637.02
    F7 = 2793.83
    G7 = 3135.96
    A7 = 3520.00
    B7 = 3951.07


Pitch = TypeVar('Pitch', int, Note)


class PiezoInterface(metaclass=ABCMeta):
    """An interface containing the methods required to control an piezo."""

    @abstractmethod
    def buzz(self, board: Board, identifier: int,
             duration: timedelta, pitch: Pitch) -> None:
        """Queue a pitch to be played."""
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

    def buzz(self, board: Board, identifier: int,
             duration: timedelta, pitch: Pitch) -> None:
        """Queue a note to be played."""
        self._backend.buzz(board, identifier, duration, pitch)
