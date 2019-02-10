"""The base classes for boards and group of boards."""

import atexit
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Dict, Iterator, List, Type

from j5.backends import Backend

if TYPE_CHECKING:
    from j5.components import Component  # noqa


class Board(metaclass=ABCMeta):
    """A collection of hardware that has an implementation."""

    # BOARDS is a list of currently instantiated boards.
    # This is useful to know so that we can make them safe in a crash.
    BOARDS: List['Board'] = []

    def __str__(self) -> str:
        """A string representation of this board."""
        return f"{self.name} - {self.serial}"

    def __new__(cls, *args, **kwargs):
        """Ensure any instantiated board is added to the boards list."""
        instance = super().__new__(cls)
        Board.BOARDS.append(instance)
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

    @abstractmethod
    def make_safe(self):
        """Make all components on this board safe."""
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    @abstractmethod
    def supported_components() -> List[Type['Component']]:
        """The types of component supported by this board."""
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    @abstractmethod
    def discover(backend: Backend) -> List['Board']:
        """Detect and return a list of boards of this type."""
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    @atexit.register
    def make_all_safe():
        """Make all boards safe."""
        for board in Board.BOARDS:
            board.make_safe()


class BoardGroup:
    """A group of boards that can be accessed."""

    def __init__(self, board: Board, backend: Backend):
        self.board_class: Board = board
        self._backend: Backend = backend
        self._iterator_counter: int = 0
        self.boards: Dict[str, Board] = {}

        self.update_boards()

    def update_boards(self) -> None:
        """Update the boards in this group to see if new boards have been added."""
        self.boards: Dict[str, Board] = {}
        for board in self.board_class.discover(self._backend):
            self.boards.update({board.serial: board})

    def singular(self) -> Board:
        """If there is only a single board in the group, return that board."""
        if len(self) == 1:
            return list(self.boards.values())[0]
        raise Exception("There is more than one or zero boards connected.")

    def make_safe(self):
        """Make all of the boards safe."""
        for board in self.boards:
            board.make_safe()

    def __len__(self) -> int:
        """Get the number of boards in this group."""
        return len(self.boards)

    def __iter__(self) -> Iterator[Board]:
        """Iterate over the boards in the group."""
        self._iterator_counter = (
            0
        )  # Reset the iteration counter. This will break if you iterate simultaneously.
        return self

    def __next__(self) -> Board:
        """Get the next item in the iteration."""
        if self._iterator_counter >= len(self.boards):
            raise StopIteration
        board = list(self.boards.values())[self._iterator_counter]
        self._iterator_counter += 1
        return board

    def __getitem__(self, serial: str):
        """Get the board from serial."""
        try:
            return self.boards[serial]
        except KeyError:
            if type(serial) != str:
                raise TypeError("Serial must be a string")
            raise KeyError(f"Could not find a board with the serial {serial}")
