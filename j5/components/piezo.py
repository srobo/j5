"""Classes for Piezo support."""

from abc import abstractmethod
from datetime import timedelta
from enum import IntEnum
from typing import Generator, Type, Union

from j5.boards import Board
from j5.components.component import Component, Interface


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
    def buzz(self, identifier: int,
             duration: timedelta, frequency: int) -> None:
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
        self.verify_pitch(pitch)
        self.verify_duration(duration)
        self._backend.buzz(self._identifier, duration, pitch)

    @staticmethod
    def verify_pitch(pitch: Pitch) -> None:
        """Verify that a pitch is valid."""
        # Verify that the type is correct.
        pitch_is_int = type(pitch) is int
        pitch_is_note = type(pitch) is Note
        if not (pitch_is_int or pitch_is_note):
            raise TypeError("Pitch must be int or Note")

        # Verify the length of the pitch is non-zero
        if pitch < 0:
            raise ValueError("Frequency must be greater than zero")

    @staticmethod
    def verify_duration(duration: timedelta) -> None:
        """Verify that a duration is valid."""
        if not isinstance(duration, timedelta):
            raise TypeError("Duration must be of type datetime.timedelta")
        if duration < timedelta(seconds=0):
            raise ValueError("Duration must be greater than or equal to zero.")
