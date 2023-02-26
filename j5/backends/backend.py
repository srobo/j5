"""The base classes for backends."""

import inspect
import logging
from abc import ABCMeta, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, Any

from j5.exceptions import j5Exception

if TYPE_CHECKING:  # pragma: nocover
    from j5.boards import Board  # noqa


class CommunicationError(j5Exception):
    """
    A communication error occurred.

    This error is thrown when there is an error communicating with a board, if a more
    specific exception is available, then that may be thrown instead, but it should
    inherit from this one.
    """


def _wrap_method_with_logging(
    backend_class: type['Backend'],
    method_name: str,
    logger: logging.Logger,
) -> None:
    old_method = getattr(backend_class, method_name)
    signature = inspect.signature(old_method)

    @wraps(old_method)
    def new_method(*args: Any, **kwargs: Any) -> Any:
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


def _wrap_methods_with_logging(backend_class: type['Backend']) -> None:
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

    def __new__(cls, name: Any, bases: Any, namespace: Any, **kwargs: Any) -> Any:
        """
        Create a new class object.

        :returns: a new backend object.
        """
        new_cls = super().__new__(cls, name, bases, namespace, **kwargs)

        if new_cls.__name__ == "Backend":
            return new_cls

        # Check if this is an abstract Backend.
        if getattr(new_cls, "__abstractmethods__", None):
            return new_cls

        # Check if this is a discovery only Backend.
        if len(new_cls.__bases__) <= 1 and new_cls.discover_only:  # type: ignore
            return new_cls

        cls._check_component_interfaces(new_cls)
        _wrap_methods_with_logging(new_cls)  # type: ignore

        return new_cls

    def _check_component_interfaces(cls) -> None:
        """
        Check that the backend has the right interfaces.

        Certain interfaces are required to support components,
        and we want to make sure that the Backend implements
        them. This is a run-time type check.

        :raises TypeError: The backend class doesn't have a required interface.
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

    discover_only = False

    @classmethod
    @abstractmethod
    def discover(cls) -> set['Board']:
        """Discover boards that this backend can control."""
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def board(self) -> type['Board']:
        """Type of board this backend implements."""
        raise NotImplementedError  # pragma: no cover

    @property
    def firmware_version(self) -> str | None:
        """
        The firmware version of the board.

        :returns: None
        """
        return None

    def get_features(self) -> set['Board.AvailableFeatures']:
        """
        The set of features available on this backend.

        :returns: The set of features available on this backend.
        """
        return set()
