"""The base classes for backends."""

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Type

if TYPE_CHECKING:
    from j5.boards import Board  # noqa


class BackendMeta(ABCMeta):
    """
    The metaclass for a backend.

    Responsible for registering the board-backend mapping with an Environment.

    """

    def __new__(mcs, name, bases, namespace, **kwargs):  # type:ignore
        """Create a new class object."""
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)  # type: ignore

        if cls.__name__ == "Backend":
            return cls

        if hasattr(cls, "environment"):
            if cls.environment is not None and cls.board is not None:

                if type(cls.environment) != Environment:
                    raise ValueError("The environment must be of type Environment.")

                if cls.board in cls.environment.supported_boards:
                    raise RuntimeError("You cannot register multiple backends for the same board in the same Environment.")  # noqa: E501

                for component in cls.board.supported_components():
                    if not issubclass(cls, component.interface_class()):
                        raise TypeError("The backend class doesn't have a required interface.")  # noqa: E501

                cls.environment.register_backend(cls.board, cls)
                return cls

        raise RuntimeError(f"The {str(cls)} has no environment attribute")


class Backend(metaclass=BackendMeta):
    """
    The base class for a backend.

    A backend is an implementation of a specific board for an environment.

    """

    @property
    @abstractmethod
    def environment(self) -> 'Environment':
        """Environment the backend belongs too."""
        raise NotImplementedError  # pragma: no cover


class Environment:
    """
    A collection of board implementations that can work together.

    Auto-populated with board mappings using metaclass magic.
    """

    def __init__(self, name: str):
        self.name = name
        self.board_backend_mapping: Dict[Type['Board'], Type[Backend]] = {}

    @property
    def supported_boards(self) -> List[Type['Board']]:
        """The boards that are supported by this backend group."""
        return list(self.board_backend_mapping.keys())

    def __str__(self) -> str:
        """Get a string representation of this group."""
        return self.name

    def register_backend(self, board: Type['Board'], backend: Type[Backend]) -> None:
        """Register a new backend with this Backend Group."""
        self.board_backend_mapping[board] = backend

    def get_backend(self, board: 'Type[Board]') -> Backend:
        """Get the backend for a board."""
        if board not in self.supported_boards:
            raise NotImplementedError(f"The {str(self)} does not support {str(board)}")

        return self.board_backend_mapping[board]()
