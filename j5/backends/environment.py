"""Environment class and related functions."""

from typing import Dict, Set, Type, TypeVar, cast

from j5.backends import Backend
from j5.boards import Board, BoardGroup

BoardT = TypeVar("BoardT", bound=Board)


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
        """
        The boards that are supported by this environment.

        :returns: set of boards that are supported by this environment.
        """
        return set(self.board_backend_mapping.keys())

    def __str__(self) -> str:
        """
        Get a string representation of this environment.

        :returns: name of the environment.
        """
        return self.name

    def register_backend(self, backend: Type[Backend]) -> None:
        """
        Register a new backend with this environment.

        :param backend: The backend to register in the environment.
        :raises RuntimeError: The backend has already been registered.
        """
        board_type: Type['Board'] = cast(Type['Board'], backend.board)
        if board_type in self.board_backend_mapping.keys():
            raise RuntimeError(f"Attempted to register multiple backends for"
                               f" {board_type.__name__} in the same environment.")
        self.board_backend_mapping[board_type] = backend

    def get_backend(self, board: Type['Board']) -> Type[Backend]:
        """
        Get the backend for a board.

        :param board: board type to fetch a backend for.
        :returns: Backend in this environment for the given board.
        :raises NotImplementedError: The environment does not support the board.
        """
        if board not in self.supported_boards:
            raise NotImplementedError(f"The {str(self)} does not support {str(board)}")

        return self.board_backend_mapping[board]

    def get_board_group(self, board: Type[BoardT]) -> 'BoardGroup[BoardT, Backend]':
        """
        Get a board group for the given board type.

        :param board: board type to fetch a backend for.
        :returns: BoardGroup in this environment for the given board.
        :raises NotImplementedError: The environment does not support the board.
        """
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

        :param other: environment to merge into this one.
        :raises RuntimeError: a board was implemented in both backends, conflict.
        """
        intersection = self.supported_boards & other.supported_boards

        if len(intersection) > 0:
            common_boards = ", ".join(x.__name__ for x in intersection)
            raise RuntimeError(
                f"Attempted to merge two Environments"
                f" that both contain: {common_boards}")
        self.board_backend_mapping = {
            **self.board_backend_mapping,
            **other.board_backend_mapping,
        }
