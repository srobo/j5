"""Classes for Motor Output support."""

from abc import abstractmethod
from enum import Enum
from typing import Type, Union

from j5.boards import Board
from j5.components.component import Component, Interface


class MotorOutputSpecialState(Enum):
    """An enum of the special states that a motor can be set to."""

    COAST = 0
    BRAKE = 1


MotorOutputState = Union[float, MotorOutputSpecialState]


class MotorOutputInterface(Interface):
    """An interface containing the methods required to control a motor board."""

    @abstractmethod
    def get_motor_output_power(self, identifier: int) -> MotorOutputState:
        """Get the motor output power, if it is on."""
        pass

    @abstractmethod
    def set_motor_output_power(self, identifier: int, power: MotorOutputState) -> None:
        """Set the motor output power."""
        pass


class MotorOutput(Component):
    """Brushed DC motor output."""

    def __init__(
            self,
            identifier: int,
            board: Board,
            backend: MotorOutputInterface,
    ) -> None:
        self._board = board
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class() -> Type[Interface]:
        """Get the interface class that is required to use this component."""
        return MotorOutputInterface

    @property
    def power(self) -> MotorOutputState:
        """Get the current power of this output."""
        return self._backend.get_motor_output_power(self._identifier)

    @power.setter
    def power(self, new_state: MotorOutputState) -> None:
        """Set the current power of this output."""
        if isinstance(new_state, float):
            if new_state < -1 or new_state > 1:
                raise ValueError("Motor Power must be between 1 and -1.")
        self._backend.set_motor_output_power(self._identifier, new_state)
