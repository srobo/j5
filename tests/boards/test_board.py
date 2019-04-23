"""Test the base classes for boards."""
from typing import TYPE_CHECKING, Optional, Set, Type

import pytest

from j5.backends import Backend, Environment
from j5.boards.board import Board, BoardGroup

if TYPE_CHECKING:
    from j5.components import Component  # noqa


class MockBoard(Board):
    """A testing board with little to no functionality."""

    def __init__(self, serial: str):
        self._serial = serial
        self._safe = False

    @property
    def name(self) -> str:
        """Get the name of this board."""
        return "Testing Board"

    @property
    def serial(self) -> str:
        """Get the serial number of this board."""
        return self._serial

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of this board."""
        return None

    def make_safe(self) -> None:
        """Make this board safe."""
        self._safe = True

    @staticmethod
    def supported_components() -> Set[Type["Component"]]:
        """List the types of component supported by this Board."""
        return set()


class MockBoardWithConstructor(MockBoard):
    """A testing board with a constructor."""

    def __init__(self, test_param: str, another_param: str,
                 one_that_defaults: bool = True) -> None:
        self.test_param = test_param
        self.another_param = another_param
        self.one_that_defaults = one_that_defaults


class NoBoardMockBackend(Backend):
    """This backend never finds any testing boards."""

    environment = Environment("MockEnvironment")
    board = MockBoard

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return None

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover boards available on this backend."""
        return set()


class OneBoardMockBackend(Backend):
    """This backend finds exactly one."""

    environment = Environment("MockEnvironment")
    board = MockBoard

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return None

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover boards available on this backend."""
        return {MockBoard("TESTSERIAL1")}


class TwoBoardsMockBackend(Backend):
    """This backend finds exactly two."""

    environment = Environment("MockEnvironment")
    board = MockBoard

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return None

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover boards available on this backend."""
        return {MockBoard("TESTSERIAL1"), MockBoard("TESTSERIAL2")}


def test_testing_board_instantiation() -> None:
    """Test that we can instantiate the testing board."""
    MockBoard("TESTSERIAL1")


def test_testing_board_instantiation_with_constructor() -> None:
    """Test that we can instantiate a board that has a constructor."""
    board = MockBoardWithConstructor("test", another_param="test2")
    assert board.test_param == "test"
    assert board.another_param == "test2"
    assert board.one_that_defaults is True


def test_testing_board_name() -> None:
    """Test the name property of the board class."""
    tb = MockBoard("TESTSERIAL1")

    assert tb.name == "Testing Board"
    assert type(tb.name) == str


def test_testing_board_serial() -> None:
    """Test the serial property of the board class."""
    tb = MockBoard("TESTSERIAL1")

    assert tb.serial == "TESTSERIAL1"
    assert type(tb.serial) == str


def test_testing_board_str() -> None:
    """Test the __str__ method of the board class."""
    tb = MockBoard("TESTSERIAL1")

    assert str(tb) == f"Testing Board - TESTSERIAL1"


def test_testing_board_repr() -> None:
    """Test the __repr__ method of the board class."""
    tb = MockBoard("TESTSERIAL1")
    assert repr(tb) == f"<MockBoard serial=TESTSERIAL1>"


def test_discover() -> None:
    """Test that the detect all static method works."""
    assert NoBoardMockBackend.discover() == set()
    assert len(OneBoardMockBackend.discover()) == 1
    assert len(TwoBoardsMockBackend.discover()) == 2


def test_testing_board_added_to_boards_list() -> None:
    """Test that an instantiated board is added to the boards list."""
    board = MockBoard("TESTSERIAL1")
    assert board in Board.BOARDS


def test_create_boardgroup() -> None:
    """Test that we can create a board group of testing boards."""
    board_group = BoardGroup[MockBoard](NoBoardMockBackend)
    assert type(board_group) == BoardGroup


def test_board_group_update() -> None:
    """Test that we can create a board group of testing boards."""
    board_group = BoardGroup[MockBoard](NoBoardMockBackend)
    board_group.update_boards()


def test_board_group_singular() -> None:
    """Test that the singular function works on a board group."""
    board_group = BoardGroup[MockBoard](OneBoardMockBackend)

    assert type(board_group.singular()) == MockBoard


def test_board_group_str() -> None:
    """Test that the board group can be represented as a string."""
    assert str(BoardGroup[MockBoard](NoBoardMockBackend)) == "Group of Boards - []"
    assert str(BoardGroup[MockBoard](OneBoardMockBackend)) == \
        "Group of Boards - [Testing Board - TESTSERIAL1]"
    assert str(BoardGroup[MockBoard](TwoBoardsMockBackend)) == \
        "Group of Boards - [Testing Board - TESTSERIAL1, Testing Board - TESTSERIAL2]"


def test_board_group_singular_but_multiple_boards() -> None:
    """Test that the singular function gets upset if there are multiple boards."""
    board_group = BoardGroup[MockBoard](TwoBoardsMockBackend)

    with pytest.raises(Exception):
        board_group.singular()


def test_board_group_boards() -> None:
    """Test that the boards property works on a board group."""
    board_group = BoardGroup[MockBoard](OneBoardMockBackend)

    assert len(board_group._boards) == 1
    assert type(list(board_group._boards
                .values())[0]) == MockBoard


def test_board_group_boards_multiple() -> None:
    """Test that the boards property works on multiple boards."""
    board_group = BoardGroup[MockBoard](TwoBoardsMockBackend)

    assert len(board_group._boards) == 2
    assert type(list(board_group._boards
                .values())[0]) == MockBoard


def test_board_group_boards_zero() -> None:
    """Test that the boards property works with no boards."""
    board_group = BoardGroup[MockBoard](NoBoardMockBackend)

    assert len(board_group._boards) == 0

    with pytest.raises(KeyError):
        board_group._boards["SERIAL0"]


def test_board_group_board_by_serial() -> None:
    """Test that the boards property works with serial indices."""
    board_group = BoardGroup[MockBoard](OneBoardMockBackend)
    BoardGroup[MockBoard](OneBoardMockBackend)

    assert type(board_group[list(board_group._boards.values())[0].serial]) == MockBoard


def test_board_group_board_by_unknown() -> None:
    """Test that the boards property throws an exception with unknown indices."""
    board_group = BoardGroup[MockBoard](OneBoardMockBackend)

    with pytest.raises(TypeError):
        board_group[0]  # type: ignore

    with pytest.raises(KeyError):
        board_group[""]

    with pytest.raises(TypeError):
        board_group[{}]  # type: ignore

    with pytest.raises(KeyError):
        board_group["ARGHHHJ"]


def test_board_group_length_zero() -> None:
    """Test that the length operator works with no boards."""
    board_group = BoardGroup[MockBoard](NoBoardMockBackend)

    assert len(board_group) == 0


def test_board_group_length() -> None:
    """Test that the length operator works on a board group."""
    board_group = BoardGroup[MockBoard](OneBoardMockBackend)

    assert len(board_group) == 1


def test_board_group_length_multiple() -> None:
    """Test that the length operator works on multiple boards."""
    board_group = BoardGroup[MockBoard](TwoBoardsMockBackend)

    assert len(board_group) == 2


def test_board_group_get_backend_class() -> None:
    """Test that the Backend class getter works."""
    board_group = BoardGroup[MockBoard](TwoBoardsMockBackend)

    assert board_group.backend_class is TwoBoardsMockBackend


def test_board_group_get_boards() -> None:
    """Test that the boards list getter works."""
    board_group = BoardGroup[MockBoard](TwoBoardsMockBackend)

    assert type(board_group.boards) is list
    assert len(board_group.boards) == 2
    assert type(board_group.boards[0]) is MockBoard


def test_board_group_contains() -> None:
    """Test that __contains__ behaves as expected."""
    board_group = BoardGroup[MockBoard](TwoBoardsMockBackend)
    assert "TESTSERIAL1" in board_group
    assert "TESTSERIAL2" in board_group
    assert "TESTSERIAL3" not in board_group


def test_board_group_iteration() -> None:
    """Test that we can iterate over a BoardGroup."""
    board_group = BoardGroup[MockBoard](TwoBoardsMockBackend)

    count = 0

    for b in board_group:
        assert type(b) == MockBoard
        count += 1

    assert count == 2


def test_board_group_iteration_sorted_by_serial() -> None:
    """Test that the boards yielded by iterating over a BoardGroup are sorted."""
    board_group = BoardGroup[MockBoard](TwoBoardsMockBackend)
    serials = [board.serial for board in board_group]
    assert len(serials) == 2
    assert serials[0] < serials[1]


def test_board_group_simultaneous_iteration() -> None:
    """Test that iterators returned by iter(BoardGroup) are independent."""
    board_group = BoardGroup[MockBoard](TwoBoardsMockBackend)
    iter1 = iter(board_group)
    iter2 = iter(board_group)
    assert next(iter1) is board_group["TESTSERIAL1"]
    assert next(iter2) is board_group["TESTSERIAL1"]
    assert next(iter1) is board_group["TESTSERIAL2"]
    assert next(iter2) is board_group["TESTSERIAL2"]


def test_board_group_make_safe() -> None:
    """Test that the make_safe function is called on all Boards in a BoardGroup."""
    board_group = BoardGroup[MockBoard](TwoBoardsMockBackend)

    assert not any(board._safe for board in board_group)
    board_group.make_safe()
    assert all(board._safe for board in board_group)
