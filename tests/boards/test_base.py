"""Test the base classes for boards."""
import pytest

from j5.backends import Backend, Environment
from j5.boards.base import Board, BoardGroup


class MockBoard(Board):
    """A testing board with little to no functionality."""

    def __init__(self, serial: str):
        self._serial = serial

    @property
    def name(self) -> str:
        """Get the name of this board."""
        return "Testing Board"

    @property
    def serial(self) -> str:
        """Get the serial number of this board."""
        return self._serial

    def make_safe(self):
        """Make this board safe."""
        pass

    @staticmethod
    def supported_components():
        """List the types of component supported by this Board."""
        return []

    @staticmethod
    def discover(backend: Backend):
        """Detect all boards of this type that are attached."""
        return backend.get_testing_boards()


class MockBoardWithConstructor(MockBoard):
    """A testing board with a constructor."""

    def __init__(self, test_param, another_param, one_that_defaults=True):
        self.test_param = test_param
        self.another_param = another_param
        self.one_that_defaults = one_that_defaults


class NoBoardMockBackend(Backend):
    """This backend never finds any testing boards."""

    environment = Environment("MockEnvironment")
    board = MockBoard

    def get_testing_boards(self):
        """Get the connected MockBoards."""
        return []


class OneBoardMockBackend(Backend):
    """This backend finds exactly one."""

    environment = Environment("MockEnvironment")
    board = MockBoard

    def get_testing_boards(self):
        """Get the connected MockBoards."""
        return [MockBoard("TESTSERIAL1")]


class TwoBoardsMockBackend(Backend):
    """This backend finds exactly two."""

    environment = Environment("MockEnvironment")
    board = MockBoard

    def get_testing_boards(self):
        """Get the connected MockBoards."""
        # These serial numbers are deliberately in reverse lexiographic order, to ensure
        # that sorting the boards (as tested by
        # test_board_group_iteration_sorted_by_serial) actually has an effect.
        return [MockBoard("TESTSERIAL2"), MockBoard("TESTSERIAL1")]


def test_testing_board_instantiation():
    """Test that we can instantiate the testing board."""
    MockBoard("TESTSERIAL1")


def test_testing_board_instantiation_with_constructor():
    """Test that we can instantiate a board that has a constructor."""
    board = MockBoardWithConstructor("test", another_param="test2")
    assert board.test_param == "test"
    assert board.another_param == "test2"
    assert board.one_that_defaults is True


def test_testing_board_name():
    """Test the name property of the board class."""
    tb = MockBoard("TESTSERIAL1")

    assert tb.name == "Testing Board"
    assert type(tb.name) == str


def test_testing_board_serial():
    """Test the serial property of the board class."""
    tb = MockBoard("TESTSERIAL1")

    assert tb.serial == "TESTSERIAL1"
    assert type(tb.serial) == str


def test_testing_board_str():
    """Test the __str__ method of the board class."""
    tb = MockBoard("TESTSERIAL1")

    assert str(tb) == f"Testing Board - TESTSERIAL1"


def test_testing_board_repr():
    """Test the __repr__ method of the board class."""
    tb = MockBoard("TESTSERIAL1")
    assert repr(tb) == f"<MockBoard serial=TESTSERIAL1>"


def test_discover():
    """Test that the detect all static method works."""
    assert MockBoard.discover(NoBoardMockBackend()) == []
    assert len(MockBoard.discover(OneBoardMockBackend())) == 1
    assert len(MockBoard.discover(TwoBoardsMockBackend())) == 2


def test_testing_board_added_to_boards_list():
    """Test that an instantiated board is added to the boards list."""
    board = MockBoard("TESTSERIAL1")
    assert board in Board.BOARDS


def test_create_boardgroup():
    """Test that we can create a board group of testing boards."""
    board_group = BoardGroup(MockBoard, NoBoardMockBackend())
    assert type(board_group) == BoardGroup


def test_board_group_update():
    """Test that we can create a board group of testing boards."""
    board_group = BoardGroup(MockBoard, NoBoardMockBackend())
    board_group.update_boards()


def test_board_group_singular():
    """Test that the singular function works on a board group."""
    board_group = BoardGroup(MockBoard, OneBoardMockBackend())

    assert type(board_group.singular()) == MockBoard


def test_board_group_singular_but_multiple_boards():
    """Test that the singular function gets upset if there are multiple boards."""
    board_group = BoardGroup(MockBoard, TwoBoardsMockBackend())

    with pytest.raises(Exception):
        board_group.singular()


def test_board_group_boards():
    """Test that the boards property works on a board group."""
    board_group = BoardGroup(MockBoard, OneBoardMockBackend())

    assert len(board_group.boards) == 1
    assert type(list(board_group.boards
                .values())[0]) == MockBoard


def test_board_group_boards_multiple():
    """Test that the boards property works on multiple boards."""
    board_group = BoardGroup(MockBoard, TwoBoardsMockBackend())

    assert len(board_group.boards) == 2
    assert type(list(board_group.boards
                .values())[0]) == MockBoard


def test_board_group_boards_zero():
    """Test that the boards property works with no boards."""
    board_group = BoardGroup(MockBoard, NoBoardMockBackend())

    assert len(board_group.boards) == 0

    with pytest.raises(KeyError):
        board_group.boards["SERIAL0"]


def test_board_group_board_by_serial():
    """Test that the boards property works with serial indices."""
    board_group = BoardGroup(MockBoard, OneBoardMockBackend())
    BoardGroup(MockBoard, OneBoardMockBackend())

    assert type(board_group[list(board_group.boards.values())[0].serial]) == MockBoard


def test_board_group_board_by_unknown():
    """Test that the boards property throws an exception with unknown indices."""
    board_group = BoardGroup(MockBoard, OneBoardMockBackend())

    with pytest.raises(TypeError):
        board_group[0]

    with pytest.raises(KeyError):
        board_group[""]

    with pytest.raises(TypeError):
        board_group[{}]

    with pytest.raises(KeyError):
        board_group["ARGHHHJ"]


def test_board_group_length():
    """Test that the length operator works on a board group."""
    board_group = BoardGroup(MockBoard, OneBoardMockBackend())

    assert len(board_group) == 1


def test_board_group_length_multiple():
    """Test that the length operator works on multiple boards."""
    board_group = BoardGroup(MockBoard, TwoBoardsMockBackend())

    assert len(board_group) == 2


def test_board_group_length_zero():
    """Test that the length operator works with no boards."""
    board_group = BoardGroup(MockBoard, NoBoardMockBackend())

    assert len(board_group) == 0


def test_board_group_iteration():
    """Test that we can iterate over a BoardGroup."""
    board_group = BoardGroup(MockBoard, TwoBoardsMockBackend())

    count = 0

    for b in board_group:
        assert type(b) == MockBoard
        count += 1

    assert count == 2


def test_board_group_iteration_sorted_by_serial():
    """Test that the boards yielded by iterating over a BoardGroup are sorted by serial number."""
    board_group = BoardGroup(MockBoard, TwoBoardsMockBackend())
    serials = [board.serial for board in board_group]
    assert len(serials) == 2
    assert serials[0] < serials[1]


def test_board_group_simultaneous_iteration():
    """Test that iterators returned by iter(BoardGroup) are independent."""
    board_group = BoardGroup(MockBoard, TwoBoardsMockBackend())
    iter1 = iter(board_group)
    iter2 = iter(board_group)
    assert next(iter1) is board_group["TESTSERIAL1"]
    assert next(iter2) is board_group["TESTSERIAL1"]
    assert next(iter1) is board_group["TESTSERIAL2"]
    assert next(iter2) is board_group["TESTSERIAL2"]
