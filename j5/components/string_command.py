"""Classes for the string command component."""

from abc import abstractmethod
from typing import Type

from j5.components.component import Component, Interface


class StringCommandComponentInterface(Interface):
    """An interface containing the methods required for string commands."""

    @abstractmethod
    def execute_string_command(self, command: str) -> str:
        """
        Execute the string command and return the result.

        This function can be synchronous and blocking.

        :param command: command to execute.
        :returns: result
        """
        raise NotImplementedError  # pragma: no cover


class StringCommandComponent(Component):
    """
    A string command component.

    This component allows the sending and receiving of commands to a
    board, so that custom ASCII protocols can be implemented. This is
    primarily aimed at Boards which can have custom firmware installed
    by the students that are using them.
    """

    def __init__(
            self,
            identifier: int,
            backend: StringCommandComponentInterface,
    ) -> None:
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class() -> Type[Interface]:
        """
        Get the interface class that is required to use this component.

        :returns: interface class.
        """
        return StringCommandComponentInterface

    @property
    def identifier(self) -> int:
        """
        An integer to identify the component on a board.

        :returns: component identifier.
        """
        return self._identifier

    def execute(self, command: str) -> str:
        """
        Execute the string command and return the result.

        This function can be synchronous and blocking.

        :param command: command to execute.
        :returns: result of command.
        :raises ValueError: command is not valid.
        """
        if not isinstance(command, str):
            raise ValueError("A command must be a string.")

        if len(command) <= 0:
            raise ValueError("A command must not be an empty string.")

        return self._backend.execute_string_command(command)

    def __call__(self, command: str) -> str:
        """
        Let this component be used as a callable.

        Reduces code complexity in API implementation, as this component
        is unlikely to be wanted to be visible by the majority of API authors.

        :param command: command to execute.
        :returns: result of command.
        """
        return self.execute(command)
