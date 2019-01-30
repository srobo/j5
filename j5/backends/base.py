"""The base classes for backends."""

from abc import ABCMeta, abstractmethod
from typing import Any, List, Mapping


class Backend(metaclass=ABCMeta):
    """
    The base class for a backend.

    A backend is an implementation of a specific board for a specific environment.

    """


class BackendGroup(metaclass=ABCMeta):
    """A collection of board implementations that can work together."""

    @property
    @abstractmethod
    def board_backend_mapping(self) -> Mapping[Any, Backend]:
        """A mapping of a supported board to a supported backend."""
        raise NotImplementedError  # pragma: no cover

    @property
    def supported_boards(self) -> List:
        """The boards that are supported by this backend group."""
        return list(self.board_backend_mapping.keys())

    def get_backend(self, board: Any) -> Backend:
        """Get the backend for a board."""
        if board not in self.supported_boards:
            raise NotImplementedError(
                "The {} does not support {}".format(str(self), str(board)),
            )

        return self.board_backend_mapping[board]()  # type: ignore
