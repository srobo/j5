"""Classes for the LED support."""

from abc import ABCMeta

from j5.components import Component


class LED(Component):
    """A standard Light Emitting Diode."""


class LEDInterface(metaclass=ABCMeta):
    """An interface containing the methods required to control an LED."""
