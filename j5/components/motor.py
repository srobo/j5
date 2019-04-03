"""Classes for Motor Output support."""

from abc import abstractmethod
from enum import Enum
from typing import Type, Union

from j5.boards import Board
from j5.components.component import Component, Interface


class MotorSpecialState(Enum):
    """An enum of the special states that a motor can be set to."""

    COAST = 0
    BRAKE = 1


MotorState = Union[float, MotorSpecialState]


class MotorInterface(Interface):
    """An interface containing the methods required to control a motor board."""

    @abstractmethod
    def get_motor_power(self, identifier: int) -> MotorState:
        """Get the motor power, if it is on."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def set_motor_power(self, identifier: int, power: MotorState) -> None:
        """Set the motor power."""
        raise NotImplementedError  # pragma: no cover


class Motor(Component):
    """Brushed DC motor output."""

    def __init__(
            self,
            identifier: int,
            board: Board,
            backend: MotorInterface,
    ) -> None:
        self._board = board
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class() -> Type[Interface]:
        """Get the interface class that is required to use this component."""
        return MotorInterface

    @property
    def power(self) -> MotorState:
        """Get the current power of this output."""
        return self._backend.get_motor_power(self._identifier)

    @power.setter
    def power(self, new_state: MotorState) -> None:
        """Set the current power of this output."""
        if isinstance(new_state, float):
            if new_state < -1 or new_state > 1:
                raise ValueError("Motor Power must be between 1 and -1.")
        self._backend.set_motor_power(self._identifier, new_state)
