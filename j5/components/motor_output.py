"""Classes for Motor Output support."""

from abc import abstractmethod
from enum import Enum
from typing import Optional, Type, Union

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
    def get_motor_output_power(self, board: Board, identifier: int) -> Optional[float]:
        """Get the motor output power, if it is on."""
        pass

    @abstractmethod
    def get_motor_output_power(self, board: Board, identifier: int, power: float) -> None:
        """Set the motor output power."""
        pass

    @abstractmethod
    def set_motor_output_brake(self, board: Board, identifier: int):
        """Brake the motor output."""
        pass

    @abstractmethod
    def get_motor_output_brake(self, board: Board, identifier: int):
        """Get if the motor is braked."""
        pass

    @abstractmethod
    def set_motor_output_coast(self, board: Board, identifier: int):
        """Coast the motor output."""
        pass

    @abstractmethod
    def get_motor_output_coast(self, board: Board, identifier: int):
        """Get if the motor is coasting."""
        pass


class MotorOutput(Component):
    """Brushed DC motor output."""

    def __init__(self, identifier: int, board: Board, backend: MotorOutputInterface) -> None:
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
        return

    @power.setter
    def power(self, new_state: MotorOutputState):
        """Set the current power of this output."""
