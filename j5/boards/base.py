"""The base classes for boards and group of boards."""

from abc import ABCMeta


class BoardGroup:
    """A group of boards that can be accessed."""


class Board(metaclass=ABCMeta):
    """A collection of hardware that has an implementation."""
