"""Base classes for components."""

from abc import ABCMeta, abstractmethod
from typing import Type

from j5.exceptions import j5Exception


class Interface(metaclass=ABCMeta):
    """A base class for interfaces to inherit from."""


class Component(metaclass=ABCMeta):
    """A component is the smallest logical part of some hardware."""

    @property
    @abstractmethod
    def identifier(self) -> int:
        """An integer to identify the component on a board."""
        raise NotImplementedError  # pragma: no cover

    @classmethod
    @abstractmethod
    def interface_class(cls) -> Type[Interface]:
        """Get the interface class that is required to use this component."""
        raise NotImplementedError  # pragma: no cover


class DerivedComponent(Component):
    """
    A derived component is a component that can take another component as a parameter.

    For example, a device may be attached to various pins on the board, and this could
    vary depending on what the user wants. We solve this by passing the pins to the
    derived component.

    >>> u = Ultrasound(pin_0, pin_1)
    """

    @property
    def identifier(self) -> int:
        """
        An integer to identify the component on a board.

        :raises NotSupportedByComponentError: derived components have no id.
        """
        raise NotSupportedByComponentError(
            "The identifier of a derived component is a ",
            "function of the components that it consists of",
        )

    @staticmethod
    @abstractmethod
    def interface_class() -> Type[Interface]:
        """
        Get the interface class that is required to use this component.

        :returns: interface class.
        """
        raise NotImplementedError  # pragma: no cover


class NotSupportedByComponentError(j5Exception):
    """This is thrown when hardware does not support the action that is attempted."""

    pass
