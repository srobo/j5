"""Classes for supporting Servomotors."""

from abc import abstractmethod
from typing import Type, Union

from j5.components.component import Component, Interface

# A servo can be powered down by setting its position to None.
ServoPosition = Union[float, None]


class ServoInterface(Interface):
    """An interface containing the methods required to control a Servo."""

    @abstractmethod
    def get_servo_position(self, identifier: int) -> ServoPosition:
        """
        Get the position of a servo.

        :param identifier: Port of servo to check.
        :returns: Position of servo.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def set_servo_position(
            self,
            identifier: int,
            position: ServoPosition,
    ) -> None:
        """
        Set the position of a servo.

        :param identifier: Port of servo to set position.
        :param position: Position to set the servo to.
        """
        raise NotImplementedError  # pragma: no cover


class Servo(Component):
    """A standard servomotor."""

    def __init__(self, identifier: int, backend: ServoInterface) -> None:
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class() -> Type[ServoInterface]:
        """
        Get the interface class that is required to use this component.

        :returns: interface class.
        """
        return ServoInterface

    @property
    def identifier(self) -> int:
        """
        An integer to identify the component on a board.

        :returns: component identifier.
        """
        return self._identifier

    @property
    def position(self) -> ServoPosition:
        """
        Get the current position of the Servo.

        :returns: current position of the Servo
        """
        return self._backend.get_servo_position(self._identifier)

    @position.setter
    def position(self, new_position: ServoPosition) -> None:
        """
        Set the position of the Servo.

        :param new_position: new position for the servo.
        :raises ValueError: invalid servo position
        """
        if new_position is not None:
            if not -1 <= new_position <= 1:
                raise ValueError
        self._backend.set_servo_position(self._identifier, new_position)
