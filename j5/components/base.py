"""Base classes for components."""

from typing import Type
from abc import ABCMeta, abstractmethod


class Interface(metaclass=ABCMeta):
    """A small useless class"""


class Component(metaclass=ABCMeta):
    """A component is the smallest logical part of some hardware."""

    @staticmethod
    @abstractmethod
    def interface_class() -> Type[Interface]:
        """Get the interface class that is required to use this component."""
        raise NotImplementedError  # pragma: no cover
