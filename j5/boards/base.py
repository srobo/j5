"""The base classes for boards and group of boards."""

from abc import ABCMeta, abstractmethod
from typing import Iterator, Union

from j5.backends import Backend

BoardIndex = Union[int, str]


class Board(metaclass=ABCMeta):
    """A collection of hardware that has an implementation."""

    def __str__(self) -> str:
        """A string representation of this board."""
        return "{} - {}".format(self.name, self.serial)

    def __repr__(self) -> str:
        """A representation of this board."""
        return "<{} serial={}>".format(self.__class__.__name__, self.serial)

    @property
    @abstractmethod
    def name(self) -> str:
        """A human friendly name for this board."""
        raise NotImplementedError

    @property
    @abstractmethod
    def serial(self) -> str:
        """The serial number of the board."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def detect_all(backend: Backend):
        """Detect all and return a list of boards of this type."""
        raise NotImplementedError


class BoardGroup:
    """A group of boards that can be accessed."""

    def __init__(self, board: Board, backend: Backend):
        self.board_class: Board = board
        self._backend: Backend = backend
        self._iterator_counter: int = 0
        self.boards = []  # type: ignore

        self.update_boards()

    def update_boards(self) -> None:
        """Update the boards in this group to see if new boards have been added."""
        self.boards = self.board_class.detect_all(self._backend)

    def singular(self) -> Board:
        """If there is only a single board in the group, return that board."""
        if len(self) == 1:
            return self.boards[0]
        raise Exception("There is more than one board connected.")

    def __len__(self):
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
        board = self.boards[self._iterator_counter]
        self._iterator_counter += 1
        return board

    def __getitem__(self, index: BoardIndex):
        """Get the board from an index."""
        if len(self.boards) <= 0:
            raise IndexError("Could not find any boards.")

        if type(index) == int:
            return self.boards[index]  # type: ignore
        elif type(index) == str:
            for b in self.boards:
                if b.serial == index:
                    return b
            raise KeyError("Could not find a board with the serial {}".format(index))
        else:
            raise IndexError(
                "Cannot index boards with type {}".format(str(type(index))),
            )
