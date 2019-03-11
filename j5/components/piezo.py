"""Classes for Piezo support."""

from abc import abstractmethod
from datetime import timedelta
from enum import IntEnum
from typing import Generator, Type, Union

from j5.boards import Board
from j5.components import Component, Interface


class Note(IntEnum):
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
    C8 = 4186

    def __reverse__(self) -> Generator['Note', None, None]:
        # Type is ignored because of an open bug within mypy
        # https://github.com/python/typeshed/issues/1590
        # https://github.com/python/typeshed/issues/1595
        yield from reversed(self.__members__.items())  # type: ignore


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

    def buzz(self, duration: timedelta, pitch: Pitch) -> None:
        """Queue a note to be played."""
        if isinstance(pitch, int):
            frequency = pitch
        elif isinstance(pitch, Note):
            frequency = pitch.value
        else:
            raise TypeError("Pitch must be of either type int or Note")

        if frequency < 0:
            raise ValueError("Pitch must be greater than zero")
        else:
            self._backend.buzz(self._board, self._identifier, duration, pitch)
