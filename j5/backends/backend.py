"""The base classes for backends."""

import inspect
import logging
from abc import ABCMeta, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, Dict, Optional, Set, Type, cast

if TYPE_CHECKING:  # pragma: nocover
    from j5.boards import Board  # noqa


class CommunicationError(Exception):
    """
    A communication error occurred.

    This error is thrown when there is an error communicating with a board, if a more
    specific exception is available, then that may be thrown instead, but it should
    inherit from this one.
    """


def _wrap_method_with_logging(
    backend_class: Type['Backend'],
    method_name: str,
    logger: logging.Logger,
) -> None:
    old_method = getattr(backend_class, method_name)
    signature = inspect.signature(old_method)
    @wraps(old_method)
    def new_method(*args, **kwargs):  # type: ignore
        retval = old_method(*args, **kwargs)
        arg_map = signature.bind(*args, **kwargs).arguments
        args_str = ", ".join(
            f"{name}={value!r}"
            for name, value in arg_map.items()
            if name != "self"
        )
        retval_str = (f" -> {retval!r}" if retval is not None else "")
        message = f"{method_name}({args_str}){retval_str}"
        logger.debug(message)
        return retval
    setattr(backend_class, method_name, new_method)


def _wrap_methods_with_logging(backend_class: Type['Backend']) -> None:
    component_classes = backend_class.board.supported_components()  # type: ignore
    for component_class in component_classes:
        logger = logging.getLogger(component_class.__module__)
        interface_class = component_class.interface_class()
        for method_name in interface_class.__abstractmethods__:
            _wrap_method_with_logging(backend_class, method_name, logger)


class BackendMeta(ABCMeta):
    """
    The metaclass for a backend.

    Ensures that the backend implements the correct interfaces
    when instantiated. It does this by checking that the class
    inherits from the interface classes defined on the Components
    in backend.board.supported_components.
    """

    def __new__(mcs, name, bases, namespace, **kwargs):  # type:ignore
        """Create a new class object."""
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)  # type: ignore

        if cls.__name__ == "Backend":
            return cls

        # Check if this is an abstract Backend.
        if bool(cls.__abstractmethods__):
            return cls

        mcs._check_component_interfaces(cls)  # type: ignore
        _wrap_methods_with_logging(cls)

        return cls

    def _check_component_interfaces(cls):  # type: ignore
        """
        Check that the backend has the right interfaces.

        Certain interfaces are required to support components,
        and we want to make sure that the Backend implements
        them. This is a run-time type check.
        """
        for component in cls.board.supported_components():  # type: ignore
            if not issubclass(cls, component.interface_class()):
                raise TypeError("The backend class doesn't have a required interface.")  # noqa: E501


class Backend(metaclass=BackendMeta):
    """
    The base class for a backend.

    A backend is an implementation of a specific board for an environment.

    It can hold data about the actual board it is controlling. There should be a ratio
    of one instance of a Backend to one instance of a Board. The Backend object should
    not hold any references to the Board, instead having it's methods executed by the
    code for the individual Board.

    A Backend usually also implements a number of ComponentInterfaces which thus allow
    a physical component to be controlled by the abstract Component representation.
    """

    @classmethod
    @abstractmethod
    def discover(cls) -> Set['Board']:
        """Discover boards that this backend can control."""
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def board(self) -> Type['Board']:
        """Type of board this backend implements."""
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        raise NotImplementedError  # pragma: no cover


class Environment:
    """
    A collection of backends that can work together.

    A number of Backends that we wish to use in a grouping, such as those that
    all work together in hardware can be added to this group. We can then pass
    Environments to a Robot object, so that the Robot object can call different
    methods based on where it is being used.

    e.g Hardware Environment

    We have `n` boards of `n` different types. They are all physical hardware.
    We create an Environment containing the Backends to control the physical
    hardware for our boards.

    It is later realised that we want to test code without the physical hardware.
    We can add Console backends to an environment, and instantiate our Robot object
    with that environment, so that the console is manipulated rather than the hardware.

    This allows for a high degree of code reuse and ensures API compatibility in
    different situations.
    """

    def __init__(self, name: str):
        self.name = name
        self.board_backend_mapping: Dict[Type['Board'], Type[Backend]] = {}

    @property
    def supported_boards(self) -> Set[Type['Board']]:
        """The boards that are supported by this environment."""
        return set(self.board_backend_mapping.keys())

    def __str__(self) -> str:
        """Get a string representation of this group."""
        return self.name

    def register_backend(self, backend: Type[Backend]) -> None:
        """Register a new backend with this environment."""
        board_type: Type['Board'] = cast(Type['Board'], backend.board)
        if board_type in self.board_backend_mapping.keys():
            raise RuntimeError(f"Attempted to register multiple backends for"
                               f" {board_type.__name__} in the same environment.")
        self.board_backend_mapping[board_type] = backend

    def get_backend(self, board: Type['Board']) -> Type[Backend]:
        """Get the backend for a board."""
        if board not in self.supported_boards:
            raise NotImplementedError(f"The {str(self)} does not support {str(board)}")

        return self.board_backend_mapping[board]

    def get_board_group(self, board: Type[BoardT]) -> 'BoardGroup[BoardT, Backend]':
        """Get a board group for the given board type."""
        if board not in self.supported_boards:
            raise NotImplementedError(f"The {str(self)} does not support {str(board)}")

        return BoardGroup.get_board_group(
            board,
            self.get_backend(board),
        )

    def merge(self, other: 'Environment') -> None:
        """
        Merge in the board-backend mappings from another environment.

        This allows vendors to predefine Environments and API authors
        can then merge several vendor environments to get the one that
        they need for their API.

        This method will fail if any board is defined in both environments,
         as it is unclear which one has the correct mapping.
        """
        intersection = self.supported_boards & other.supported_boards

        if len(intersection) > 0:
            common_boards = ", ".join(map(lambda x: x.__name__, intersection))
            raise RuntimeError(
                f"Attempted to merge two Environments"
                f" that both contain: {common_boards}")
        self.board_backend_mapping = {
            **self.board_backend_mapping,
            **other.board_backend_mapping,
        }
