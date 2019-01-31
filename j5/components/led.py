"""Classes for the LED support."""

from abc import ABCMeta, abstractmethod

from j5.boards import Board
from j5.components import Component


class LEDInterface(metaclass=ABCMeta):
    """An interface containing the methods required to control an LED."""

    @abstractmethod
    def set_led_state(self, board: Board, identifier: int, state: bool) -> None:
        """Set the state of an LED."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def get_led_state(self, board: Board, identifier: int) -> bool:
        """Set the state of an LED."""
        raise NotImplementedError  # pragma: no cover


class LED(Component):
    """A standard Light Emitting Diode."""

    def __init__(self, identifier: int, board: Board, backend: LEDInterface) -> None:
        self._board = board
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class():
        """Get the interface class that is required to use this component."""
        return LEDInterface

    @property
    def state(self) -> bool:
        """Get the current state of the LED."""
        return self._backend.get_led_state(self._board, self._identifier)

    @state.setter
    def state(self, new_state: bool) -> None:
        """Set the state of the LED."""
        self._backend.set_led_state(self._board, self._identifier, new_state)
