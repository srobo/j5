"""Classes for Piezo support."""

from abc import abstractmethod
from datetime import timedelta
from enum import Enum
from typing import Type, Union

from j5.boards import Board
from j5.components import Component, Interface


class Note(Enum):
    """An enumeration of notes.

    An enumeration of notes from scientific pitch
    notation and their related frequencies in Hz.
    """

    C6 = 1047
    D6 = 1175
    E6 = 1319
    F6 = 1397
    G6 = 1568
    A6 = 1760
    B6 = 1976
    C7 = 2093
    D7 = 2349
    E7 = 2637
    F7 = 2794
    G7 = 3136
    A7 = 3520
    B7 = 3951


Pitch = Union[int, Note]


class PiezoInterface(Interface):
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
    def interface_class() -> Type[PiezoInterface]:
        """Get the interface class that is required to use this component."""
        return PiezoInterface

    def buzz(self, board: Board, identifier: int,
             duration: timedelta, pitch: Pitch) -> None:
        """Queue a note to be played."""
        if type(pitch) is int:
            frequency = pitch
        elif type(pitch) is Note:
            frequency = pitch.value
        else:
            raise TypeError

        if frequency < 0:
            raise ValueError
        else:
            self._backend.buzz(board, identifier, duration, pitch)
