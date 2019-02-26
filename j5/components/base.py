"""Base classes for components."""

from abc import ABCMeta, abstractmethod
from typing import Type


class Interface(metaclass=ABCMeta):
    """A base class for interfaces to inherit from."""


class Component(metaclass=ABCMeta):
    """A component is the smallest logical part of some hardware."""

    @staticmethod
    @abstractmethod
    def interface_class() -> Type[Interface]:
        """Get the interface class that is required to use this component."""
        raise NotImplementedError  # pragma: no cover


class NotSupportedByHardwareError(Exception):
    """This is thrown when hardware does not support the action that is attempted."""

    pass
