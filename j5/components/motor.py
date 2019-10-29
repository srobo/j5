"""Classes for Motor support."""

from abc import abstractmethod
from enum import Enum
from typing import Type, Union

from j5.components.component import Component, Interface


class MotorSpecialState(Enum):
    """An enum of the special states that a motor can be set to."""

    COAST = 0
    BRAKE = 1


MotorState = Union[float, MotorSpecialState]


class MotorInterface(Interface):
    """An interface containing the methods required to control a motor board."""

    @abstractmethod
    def get_motor_state(self, identifier: int) -> MotorState:
        """Get the motor state."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def set_motor_state(self, identifier: int, power: MotorState) -> None:
        """Set the motor state."""
        raise NotImplementedError  # pragma: no cover


class Motor(Component):
    """Brushed DC motor output."""

    def __init__(
            self,
            identifier: int,
            backend: MotorInterface,
    ) -> None:
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class() -> Type[Interface]:
        """Get the interface class that is required to use this component."""
        return MotorInterface

    @property
    def identifier(self) -> int:
        """An integer to identify the component on a board."""
        return self._identifier

    @property
    def power(self) -> MotorState:
        """Get the current power of this output."""
        return self._backend.get_motor_state(self._identifier)

    @power.setter
    def power(self, new_power: MotorState) -> None:
        """Set the current state of this output."""
        if not isinstance(new_power, MotorSpecialState):
            if not(-1 <= new_power <= 1):
                raise ValueError("Motor power must be between 1 and -1.")
        self._backend.set_motor_state(self._identifier, new_power)
