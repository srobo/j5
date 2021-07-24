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

from j5.backends import Backend, CommunicationError

if TYPE_CHECKING:
    from j5.boards import Board  # noqa: F401

T = TypeVar('T', bound='Board')
U = TypeVar('U', bound=Backend)


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

        :param backend: The class of backend to get.
        :returns: A BoardGroup containing all of the backends of the requested type.
        """
        return BoardGroup[T, U](backend)

    def update_boards(self) -> None:
        """Update the boards in this group to see if new boards have been added."""
        self._boards.clear()
        discovered_boards = self._backend_class.discover()
        for board in sorted(discovered_boards, key=lambda b: b.serial_number):
            self._boards.update({board.serial_number: cast(T, board)})

    def singular(self) -> T:
        """
        If there is only a single board in the group, return that board.

        :returns: The instance of the only board in the group.
        :raises CommunicationError: Multiple boards were found.
        """
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
        """
        A string representation of the board group.

        :returns: string representation of the board group.
        """
        list_str = ', '.join(map(str, self._boards.values()))

        return f"Group of Boards - [{list_str}]"

    def __repr__(self) -> str:
        """
        A representation of this board.

        :returns: string representation of the board group.
        """
        return f"BoardGroup(backend_class={self._backend_class.__name__})"

    def __len__(self) -> int:
        """
        Get the number of boards in this group.

        :returns: number of boards in this group.
        """
        return len(self._boards)

    def __contains__(self, serial_number: str) -> bool:
        """
        Check if a board is in this group.

        :param serial_number: Serial Number of the board to look for.
        :returns: True if the board with the serial number is in the group.
        """
        return serial_number in self._boards

    def __iter__(self) -> Iterator[T]:
        """
        Iterate over the boards in the group.

        The boards are ordered lexiographically by serial number.

        :returns: Iterator of all boards in the group.
        """
        return iter(self._boards.values())

    def __getitem__(self, serial_number: str) -> T:
        """
        Get the board from serial.

        :param serial_number: Serial number of the board to fetch.
        :returns: Board instance with the provided serial number.
        :raises KeyError: The board was not found.
        :raises TypeError: The serial number of the board was not a string.
        """
        try:
            return self._boards[serial_number]
        except KeyError:
            if not isinstance(serial_number, str):
                raise TypeError("Serial number must be a string")
            raise KeyError(
                f"Could not find a board with the serial number {serial_number}",
            )

    @property
    def backend_class(self) -> Type[U]:
        """
        The Backend that this group uses for Boards.

        :returns: The backend used to interact with boards.
        """
        return self._backend_class

    @property
    def boards(self) -> List[T]:
        """
        Get an unordered list of boards in this group.

        :returns: unordered list of boards in this group.
        """
        return list(self._boards.values())
