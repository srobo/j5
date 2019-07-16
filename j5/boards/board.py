"""The base classes for boards and group of boards."""

import atexit
from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from typing import (
    TYPE_CHECKING,
    Dict,
    Generic,
    Iterator,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    cast,
)

from j5.backends import Backend, CommunicationError

if TYPE_CHECKING:  # pragma: nocover
    from j5.components import Component  # noqa


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
    @atexit.register
    def make_all_safe() -> None:
        """Make all boards safe."""
        for board in Board.BOARDS:
            board.make_safe()


T = TypeVar('T', bound='Board')


class BoardGroup(Generic[T]):
    """A group of boards that can be accessed."""

    def __init__(self, backend_class: Type[Backend]):
        self._backend_class = backend_class
        self._boards: Dict[str, T] = OrderedDict()

        self.update_boards()

    def update_boards(self) -> None:
        """Update the boards in this group to see if new boards have been added."""
        self._boards.clear()
        discovered_boards = self._backend_class.discover()
        for board in sorted(discovered_boards, key=lambda b: b.serial):
            self._boards.update({board.serial: cast(T, board)})

    def singular(self) -> T:
        """If there is only a single board in the group, return that board."""
        num = len(self)
        if num == 1:
            return list(self._boards.values())[0]
        else:
            name = self._backend_class.board.__name__
            raise CommunicationError(
                f"expected exactly one {name} to be connected, but found {num}",
            )

    def make_safe(self) -> None:
        """Make all of the boards safe."""
        for board in self._boards.values():
            board.make_safe()

    def __str__(self) -> str:
        """A string representation of the board group."""
        list_str = ', '.join(map(str, self._boards.values()))

        return f"Group of Boards - [{list_str}]"

    def __repr__(self) -> str:
        """A representation of this board."""
        return f"BoardGroup(backend_class={self._backend_class.__name__})"

    def __len__(self) -> int:
        """Get the number of boards in this group."""
        return len(self._boards)

    def __contains__(self, serial: str) -> bool:
        """Check if a board is in this group."""
        return serial in self._boards

    def __iter__(self) -> Iterator[T]:
        """
        Iterate over the boards in the group.

        The boards are ordered lexiographically by serial number.
        """
        return iter(self._boards.values())

    def __getitem__(self, serial: str) -> T:
        """Get the board from serial."""
        try:
            return self._boards[serial]
        except KeyError:
            if type(serial) != str:
                raise TypeError("Serial must be a string")
            raise KeyError(f"Could not find a board with the serial {serial}")

    @property
    def backend_class(self) -> Type[Backend]:
        """The Backend that this group uses for Boards."""
        return self._backend_class

    @property
    def boards(self) -> List[T]:
        """Get an unordered list of boards in this group."""
        return list(self._boards.values())
