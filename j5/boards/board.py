"""The base classes for boards and group of boards."""

import atexit
import logging
import os
import signal
from abc import ABCMeta, abstractmethod
from types import FrameType
from typing import TYPE_CHECKING, Dict, Optional, Set, Type, TypeVar

if TYPE_CHECKING:  # pragma: nocover
    from j5.components import Component  # noqa: F401
    from typing import Callable, Union

    SignalHandler = Union[
        Callable[[signal.Signals, FrameType], None],
        int,
        signal.Handlers,
        None,
    ]

T = TypeVar('T', bound='Board')
U = TypeVar('U')  # See #489


class Board(metaclass=ABCMeta):
    """A collection of hardware that has an implementation."""

    # BOARDS is a set of currently instantiated boards.
    # This is useful to know so that we can make them safe in a crash.
    BOARDS: Set['Board'] = set()

    def __str__(self) -> str:
        """A string representation of this board."""
        return f"{self.name} - {self.serial}"

    def __new__(cls, *args, **kwargs):  # type: ignore
        """Ensure any instantiated board is added to the boards list."""
        instance = super().__new__(cls)
        Board.BOARDS.add(instance)
        return instance

    def __repr__(self) -> str:
        """A representation of this board."""
        return f"<{self.__class__.__name__} serial={self.serial}>"

    @property
    @abstractmethod
    def name(self) -> str:
        """A human friendly name for this board."""
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def serial(self) -> str:
        """The serial number of the board."""
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def make_safe(self) -> None:
        """Make all components on this board safe."""
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    @abstractmethod
    def supported_components() -> Set[Type['Component']]:
        """The types of component supported by this board."""
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def make_all_safe() -> None:
        """Make all boards safe."""
        for board in Board.BOARDS:
            board.make_safe()

    @staticmethod
    def _make_all_safe_at_exit() -> None:
        # Register make_all_safe to be called upon normal program termination.
        atexit.register(Board.make_all_safe)

        # Register make_all_safe to be called when a termination signal is received.
        old_signal_handlers: Dict[signal.Signals, SignalHandler] = {}

        def new_signal_handler(signal_type: signal.Signals, frame: FrameType) -> None:
            logging.getLogger(__name__).error("program terminated prematurely")
            Board.make_all_safe()
            # Do what the signal originally would have done.
            signal.signal(signal_type, old_signal_handlers[signal_type])
            os.kill(0, signal_type)  # 0 = current process

        for signal_type in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
            old_signal_handler = signal.signal(signal_type, new_signal_handler)
            old_signal_handlers[signal_type] = old_signal_handler


Board._make_all_safe_at_exit()
