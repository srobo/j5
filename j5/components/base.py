"""Base classes for components."""

from abc import ABCMeta, abstractmethod


class Component(metaclass=ABCMeta):
    """A component is the smallest logical part of some hardware."""

    @property
    @abstractmethod
    def interface_class(self):
        """Get the interface class that is required to use this component."""
        raise NotImplementedError  # pragma: no cover
