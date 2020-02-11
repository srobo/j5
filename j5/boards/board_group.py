"""Board Group class."""
from collections import OrderedDict
from typing import (
    TYPE_CHECKING,
    Dict,
    Generic,
    Iterator,
    List,
    Type,
    TypeVar,
    cast,
)

from j5.backends import CommunicationError

if TYPE_CHECKING:
    from j5.boards import Board  # noqa: F401

T = TypeVar('T', bound='Board')
U = TypeVar('U')  # See #489


class BoardGroup(Generic[T, U]):
    """A group of boards that can be accessed."""

    def __init__(self, backend_class: Type[U]) -> None:
        self._backend_class = backend_class
        self._boards: Dict[str, T] = OrderedDict()

        self.update_boards()

    @classmethod
    def get_board_group(cls, _: Type[T], backend: Type[U]) -> 'BoardGroup[T, U]':
        """
        Get the board group with the given types.

        Whilst the first parameter value is not actually used in the function,
        we need it for typing purposes. This is similar to how a ProxyType
        works in Haskell.
        """
        return BoardGroup[T, U](backend)

    def update_boards(self) -> None:
        """Update the boards in this group to see if new boards have been added."""
        self._boards.clear()
        # See  #489 for type ignore explanation
        discovered_boards = self._backend_class.discover()  # type: ignore
        for board in sorted(discovered_boards, key=lambda b: b.serial):
            self._boards.update({board.serial: cast(T, board)})

    def singular(self) -> T:
        """If there is only a single board in the group, return that board."""
        num = len(self)
        if num == 1:
            return list(self._boards.values())[0]
        else:
            # See  #489 for type ignore explanation
            name = self._backend_class.board.__name__  # type: ignore
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
    def backend_class(self) -> Type[U]:
        """The Backend that this group uses for Boards."""
        return self._backend_class

    @property
    def boards(self) -> List[T]:
        """Get an unordered list of boards in this group."""
        return list(self._boards.values())
