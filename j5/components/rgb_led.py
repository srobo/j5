"""Classes for RGB LED components."""

from abc import abstractmethod
from enum import Enum
from typing import Tuple, Type, Union

from j5.components.component import Component, Interface


class RGBColour(Enum):
    """The colour channels on an RGB LED."""

    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class RGBLEDInterface(Interface):
    """An interface containing the methods required to control a RGB LED."""

    @abstractmethod
    def get_rgb_led_channel_duty_cycle(
        self,
        identifier: int,
        channel: RGBColour,
    ) -> float:
        """
        Get the duty cycle of a channel on the LED.

        :param identifier: identifier of the RGB LED.
        :param channel: channel to get the duty cycle for.
        :returns: current duty cycle of the LED.
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def set_rgb_led_channel_duty_cycle(
        self,
        identifier: int,
        channel: RGBColour,
        duty_cycle: float,
    ) -> None:
        """
        Set the duty cycle of a channel on the LED.

        :param identifier: identifier of the RGB LED.
        :param channel: channel to set the duty cycle of.
        :param duty_cycle: desired duty cycle of the LED.
        """
        raise NotImplementedError  # pragma: no cover


class RGBLED(Component):
    """
    A Light Emitting Diode, driven by a PWM output.

    This usually means that the LED is of variable brightness.
    """

    def __init__(self, identifier: int, backend: RGBLEDInterface) -> None:
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class() -> Type[RGBLEDInterface]:
        """
        Get the interface class that is required to use this component.

        :returns: interface class.
        """
        return RGBLEDInterface

    @property
    def identifier(self) -> int:
        """
        An integer to identify the component on a board.

        :returns: component identifier.
        """
        return self._identifier

    def get_channel(self, channel: Union[str, RGBColour]) -> float:
        """
        Get the current value of a channel.

        :param channel: The channel to get the value for.
        :returns: The duty cycle for the channel.
        :raises ValueError: channel is not a valid RGB channel.
        """
        if isinstance(channel, str):
            try:
                colour = RGBColour(channel.lower())
            except ValueError:
                raise ValueError(
                    f"{channel} is not a RGB colour, choose from: "
                    "red, green, blue",
                )
        else:
            colour = channel

        return self._backend.get_rgb_led_channel_duty_cycle(self._identifier, colour)

    def set_channel(self, channel: Union[str, RGBColour], duty_cycle: float) -> None:
        """
        Set the current value of a channel.

        :param channel: The channel to get the value for.
        :param duty_cycle: The duty cycle to set the channel to.
        :raises ValueError: channel is not a valid RGB channel.
        :raises ValueError: duty cycle is not in expected range.
        """
        if isinstance(channel, str):
            try:
                colour = RGBColour(channel.lower())
            except ValueError:
                raise ValueError(
                    f"{channel} is not a RGB colour, choose from: "
                    "red, green, blue",
                )
        else:
            colour = channel

        if duty_cycle < 0 or duty_cycle > 1:
            raise ValueError("PWM LED duty cycle must be between 0 and 1")

        self._backend.set_rgb_led_channel_duty_cycle(
            self._identifier,
            colour,
            duty_cycle,
        )

    @property
    def rgb(self) -> Tuple[float, float, float]:
        """
        Get a tuple of the channel duty cycles.

        :returns: tuple of duty cycles (R, G, B).
        """
        return (
            self.get_channel(RGBColour.RED),
            self.get_channel(RGBColour.GREEN),
            self.get_channel(RGBColour.BLUE),
        )

    @rgb.setter
    def rgb(self, values: Tuple[float, float, float]) -> None:
        """
        Set the channels using an RGB tuple.

        :param values: An RGB tuple of duty cycles to set.
        """
        red, green, blue = values
        self.set_channel(RGBColour.RED, red)
        self.set_channel(RGBColour.GREEN, green)
        self.set_channel(RGBColour.BLUE, blue)

    @property
    def red(self) -> float:
        """
        Get the current value of the red channel.

        :returns: current duty cycle of the red channel.
        """
        return self.get_channel(RGBColour.RED)

    @red.setter
    def red(self, duty_cycle: float) -> None:
        """
        Set the duty cycle of the red channel.

        :param duty_cycle: duty cycle of the red channel.
        """
        self.set_channel(RGBColour.RED, duty_cycle)

    @property
    def green(self) -> float:
        """
        Get the current value of the green channel.

        :returns: current duty cycle of the green channel.
        """
        return self.get_channel(RGBColour.GREEN)

    @green.setter
    def green(self, duty_cycle: float) -> None:
        """
        Set the duty cycle of the green channel.

        :param duty_cycle: duty cycle of the green channel.
        """
        self.set_channel(RGBColour.GREEN, duty_cycle)

    @property
    def blue(self) -> float:
        """
        Get the current value of the blue channel.

        :returns: current duty cycle of the blue channel.
        """
        return self.get_channel(RGBColour.BLUE)

    @blue.setter
    def blue(self, duty_cycle: float) -> None:
        """
        Set the duty cycle of the blue channel.

        :param duty_cycle: duty cycle of the blue channel.
        """
        self.set_channel(RGBColour.BLUE, duty_cycle)
