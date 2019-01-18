"""The base classes for backends."""

from abc import ABCMeta, abstractmethod
from typing import Any, Mapping


class Backend(metaclass=ABCMeta):
    """
    The base class for a backend.

    A backend is an implementation of a specific board for a specific environment.

    """


class BackendGroup(metaclass=ABCMeta):
    """A collection of board implementations that can work together."""

    @property
    @abstractmethod
    def supported_boards(self) -> Mapping[Any, Backend]:
        """The boards that are supported by this backend group."""
        raise NotImplementedError

    def get_backend(self, board: Any) -> Backend:
        """Get the backend for a board."""
        if board not in self.supported_boards.keys():
            raise NotImplementedError(
                "The {} does not support {}".format(str(self), str(board)),
            )

        return self.supported_boards[board]()  # type: ignore
