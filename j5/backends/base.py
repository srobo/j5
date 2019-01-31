"""The base classes for backends."""

from abc import ABCMeta
from typing import Any, List, Mapping


class BackendMeta(ABCMeta):
    """
    The metaclass for a backend.

    Responsible for registering the backend with a BackendGroup.

    """

    def __new__(mcs, name, bases, namespace, **kwargs):
        """Create a new class object."""
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        if cls.__name__ == "Backend":
            return cls

        if hasattr(cls, "group"):
            if cls.group is not None and cls.board is not None:

                if type(cls.group) != BackendGroup:
                    raise ValueError("The Backend Group must be of type BackendGroup.")

                if cls.board in cls.group.supported_boards:
                    raise RuntimeError("You cannot register multiple backends for the same board in the same BackendGroup.")  # noqa: E501

                for component in cls.board.supported_components():
                    if not issubclass(cls, component.interface_class()):
                        raise TypeError("The backend class doesn't have a required interface.")

                cls.group.register_backend(cls.board, cls)
                return cls

        raise RuntimeError(f"The {str(cls)} has no group attribute")


class Backend(metaclass=BackendMeta):
    """
    The base class for a backend.

    A backend is an implementation of a specific board for a specific environment.

    """


class BackendGroup:
    """
    A collection of board implementations that can work together.

    Auto-populated with board mappings using metaclass magic.
    """

    def __init__(self, name: str):
        self.name = name
        self.board_backend_mapping: Mapping[Any, Backend] = {}

    @property
    def supported_boards(self) -> List[Any]:
        """The boards that are supported by this backend group."""
        return list(self.board_backend_mapping.keys())

    def __str__(self):
        """Get a string representation of this group."""
        return self.name

    def register_backend(self, board: Any, backend: Backend):
        """Register a new backend with this Backend Group."""
        self.board_backend_mapping[board] = backend

    def get_backend(self, board: Any) -> Backend:
        """Get the backend for a board."""
        if board not in self.supported_boards:
            raise NotImplementedError(f"The {str(self)} does not support {str(board)}")

        return self.board_backend_mapping[board]()  # type: ignore
