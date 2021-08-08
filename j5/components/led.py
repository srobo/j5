"""Classes for the LED support."""

from abc import abstractmethod
from typing import Type

from j5.components.component import Component, Interface


class LEDInterface(Interface):
    """An interface containing the methods required to control an LED."""

    @abstractmethod
    def get_led_state(self, identifier: int) -> bool:
        """
        Get the state of an LED.

        :param identifier: identifier of the LED.
        :returns: current state of the LED.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def set_led_state(self, identifier: int, state: bool) -> None:
        """
        Set the state of an LED.

        :param identifier: identifier of the LED.
        :param state: desired state of the LED.
        """
        raise NotImplementedError  # pragma: no cover


class LED(Component):
    """A standard Light Emitting Diode."""

    def __init__(self, identifier: int, backend: LEDInterface) -> None:
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class() -> Type[LEDInterface]:
        """
        Get the interface class that is required to use this component.

        :returns: interface class.
        """
        return LEDInterface

    @property
    def identifier(self) -> int:
        """
        An integer to identify the component on a board.

        :returns: component identifier.
        """
        return self._identifier

    @property
    def state(self) -> bool:
        """
        Get the current state of the LED.

        :returns: current state of the LED.
        """
        return self._backend.get_led_state(self._identifier)

    @state.setter
    def state(self, new_state: bool) -> None:
        """
        Set the state of the LED.

        :param new_state: state of the LED
        """
        self._backend.set_led_state(self._identifier, new_state)
