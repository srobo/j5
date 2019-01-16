"""The base classes for backends."""

from abc import ABCMeta


class BackendGroup(metaclass=ABCMeta):
    """A collection of board implementations that can work together."""


class Backend(metaclass=ABCMeta):
    """
    The base class for a backend.

    A backend is an implementation of a specific board for a specific environment.

    """
