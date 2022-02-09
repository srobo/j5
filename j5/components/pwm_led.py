"""Classes for PWM LED components."""

from abc import abstractmethod
from typing import Type

from j5.components.component import Component, Interface


class PWMLEDInterface(Interface):
    """An interface containing the methods required to control a PWM LED."""

    @abstractmethod
    def get_pwm_led_duty_cycle(self, identifier: int) -> float:
        """
        Get the duty cycle of an LED.

        :param identifier: identifier of the PWM LED.
        :returns: current duty cycle of the LED.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def set_pwm_led_duty_cycle(self, identifier: int, duty_cycle: float) -> None:
        """
        Set the duty cycle of an LED.

        :param identifier: identifier of the PWM LED.
        :param duty_cycle: desired duty cycle of the LED.
        """
        raise NotImplementedError  # pragma: no cover


class PWMLED(Component):
    """
    A Light Emitting Diode, driven by a PWM output.

    This usually means that the LED is of variable brightness.
    """

    def __init__(self, identifier: int, backend: PWMLEDInterface) -> None:
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class() -> Type[PWMLEDInterface]:
        """
        Get the interface class that is required to use this component.

        :returns: interface class.
        """
        return PWMLEDInterface

    @property
    def identifier(self) -> int:
        """
        An integer to identify the component on a board.

        :returns: component identifier.
        """
        return self._identifier

    @property
    def duty_cycle(self) -> float:
        """
        Get the current duty cycle of the LED.

        :returns: current duty cycle of the LED.
        """
        return self._backend.get_pwm_led_duty_cycle(self._identifier)

    @duty_cycle.setter
    def duty_cycle(self, new_duty_cycle: float) -> None:
        """
        Set the duty cycle of the LED.

        :param new_duty_cycle: duty cycle of the LED.
        :raises ValueError: The duty cycle was outside of the expected range.
        """
        if new_duty_cycle < 0 or new_duty_cycle > 1:
            raise ValueError("PWM LED duty cycle must be between 0 and 1")
        self._backend.set_pwm_led_duty_cycle(self._identifier, new_duty_cycle)
