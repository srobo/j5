"""Classes for Piezo support."""

from abc import abstractmethod
from datetime import timedelta
from enum import Enum
from typing import Optional, Type, Union

from j5.components.component import Component, Interface


class Note(float, Enum):
    """An enumeration of notes.

    An enumeration of notes from scientific pitch
    notation and their related frequencies in Hz.
    """

    C6 = 1047.0
    D6 = 1174.7
    E6 = 1318.5
    F6 = 1396.9
    G6 = 1568.0
    A6 = 1760.0
    B6 = 1975.5
    C7 = 2093.0
    D7 = 2349.3
    E7 = 2637.0
    F7 = 2793.8
    G7 = 3136.0
    A7 = 3520.0
    B7 = 3951.1
    C8 = 4186.0


Pitch = Union[int, float, Note]


class PiezoInterface(Interface):
    """An interface containing the methods required to control an piezo."""

    @abstractmethod
    def buzz(
        self,
        identifier: int,
        duration: timedelta,
        frequency: float,
        blocking: bool,
    ) -> None:
        """
        Queue a pitch to be played.

        A buzz can either be blocking, or non-blocking.

        If a backend does not support a non-blocking buzz, it will
        raise a :class:`j5.components.NotSupportedByComponentError`.

        :param identifier: piezo identifier to play pitch on.
        :param duration: duration of the tone.
        :param frequency: Pitch of the tone in Hz.
        :param blocking: whether the code waits for the buzz
        """
        raise NotImplementedError  # pragma: no cover


class Piezo(Component):
    """A standard piezo."""

    def __init__(
        self,
        identifier: int,
        backend: PiezoInterface,
        *,
        default_blocking: bool = False,
    ) -> None:
        self._backend = backend
        self._identifier = identifier
        self._default_blocking = default_blocking

    @staticmethod
    def interface_class() -> Type[PiezoInterface]:
        """
        Get the interface class that is required to use this component.

        :returns: interface class.
        """
        return PiezoInterface

    @property
    def identifier(self) -> int:
        """
        An integer to identify the component on a board.

        :returns: component identifier.
        """
        return self._identifier

    def buzz(
        self,
        duration: Union[int, float, timedelta],
        pitch: Pitch,
        *,
        blocking: Optional[bool] = None,
    ) -> None:
        """
        Queue a note to be played.

        Float and integer durations are measured in seconds.

        A buzz can either be blocking, or non-blocking and will fall back to
        a default if it is not specified.

        :param duration: length to play for
        :param pitch: pitch of buzz.
        :param blocking: whether the code waits for the buzz
        """
        if isinstance(duration, float) or isinstance(duration, int):
            duration = timedelta(seconds=duration)
        if type(pitch) is int:
            pitch = float(pitch)

        self.verify_pitch(pitch)
        self.verify_duration(duration)
        self._backend.buzz(
            self._identifier,
            duration,
            pitch,
            blocking or self._default_blocking,  # Fallback to component default.
        )

    @staticmethod
    def verify_pitch(pitch: Pitch) -> None:
        """
        Verify that a pitch is valid.

        :param pitch: pitch to validate.
        :raises TypeError: Pitch must be float or Note
        :raises ValueError: Frequency must be greater than zero
        """
        # Verify that the type is correct.
        pitch_is_float = type(pitch) is float
        pitch_is_note = type(pitch) is Note
        if not (pitch_is_float or pitch_is_note):
            raise TypeError("Pitch must be float or Note")

        if pitch <= 0:
            raise ValueError("Frequency must be greater than zero")

    @staticmethod
    def verify_duration(duration: timedelta) -> None:
        """
        Verify that a duration is valid.

        :param duration: duration to validate.
        :raises TypeError: duration must be a timedelta.
        :raises ValueError: duration cannot be negative.
        """
        if not isinstance(duration, timedelta):
            raise TypeError("Duration must be of type datetime.timedelta")
        if duration <= timedelta(seconds=0):
            raise ValueError("Duration must be greater than or equal to zero.")
