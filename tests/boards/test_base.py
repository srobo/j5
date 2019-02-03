"""Test the base classes for boards."""
import pytest

from j5.backends import Backend, Environment
from j5.boards.base import Board, BoardGroup


class TestingBoard(Board):
    """A testing board with little to no functionality."""

    @property
    def name(self) -> str:
        """Get the name of this board."""
        return "Testing Board"

    @property
    def serial(self) -> str:
        """Get the serial number of this board."""
        return f"SERIAL {id(self)}"

    @staticmethod
    def components():
        """List the components on this Board."""
        return []

    @staticmethod
    def discover(backend: Backend):
        """Detect all boards of this type that are attached."""
        return backend.get_testing_boards()


class NoBoardTestingBackend(Backend):
    """This backend never finds any testing boards."""

    environment = Environment("TestEnvironment")
    board = TestingBoard

    def get_testing_boards(self):
        """Get the connected TestingBoards."""
        return []


""" Instantiate testing boards to use in the backends"""
testing_board_instance_one: Board = TestingBoard()
testing_board_instance_two: Board = TestingBoard()


class OneBoardTestingBackend(Backend):
    """This backend finds exactly one."""

    environment = Environment("TestEnvironment")
    board = TestingBoard

    def get_testing_boards(self):
        """Get the connected TestingBoards."""
        return [testing_board_instance_one]


class TwoBoardsTestingBackend(Backend):
    """This backend finds exactly two."""

    environment = Environment("TestEnvironment")
    board = TestingBoard

    def get_testing_boards(self):
        """Get the connected TestingBoards."""
        return [
            testing_board_instance_one,
            testing_board_instance_two,
        ]


def test_testing_board_instantiation():
    """Test that we can instantiate the testing board."""
    TestingBoard()


def test_testing_board_name():
    """Test the name property of the board class."""
    tb = TestingBoard()

    assert tb.name == "Testing Board"
    assert type(tb.name) == str


def test_testing_board_serial():
    """Test the serial property of the board class."""
    tb = TestingBoard()

    assert tb.serial == f"SERIAL {id(tb)}"
    assert type(tb.serial) == str


def test_testing_board_str():
    """Test the __str__ method of the board class."""
    tb = TestingBoard()

    assert str(tb) == f"Testing Board - SERIAL {id(tb)}"


def test_testing_board_repr():
    """Test the __repr__ method of the board class."""
    tb = TestingBoard()

    assert repr(tb) == f"<TestingBoard serial=SERIAL {id(tb)}>"


def test_discover():
    """Test that the detect all static method works."""
    assert TestingBoard.discover(NoBoardTestingBackend()) == []
    assert TestingBoard.discover(OneBoardTestingBackend()) == (OneBoardTestingBackend()
                                                               .get_testing_boards())
    assert TestingBoard.discover(TwoBoardsTestingBackend()) == (TwoBoardsTestingBackend()
                                                                .get_testing_boards())


def test_create_boardgroup():
    """Test that we can create a board group of testing boards."""
    board_group = BoardGroup(TestingBoard, NoBoardTestingBackend())
    assert type(board_group) == BoardGroup


def test_board_group_update():
    """Test that we can create a board group of testing boards."""
    board_group = BoardGroup(TestingBoard, NoBoardTestingBackend())
    board_group.update_boards()


def test_board_group_singular():
    """Test that the singular function works on a board group."""
    board_group = BoardGroup(TestingBoard, OneBoardTestingBackend())

    assert type(board_group.singular()) == TestingBoard


def test_board_group_singular_but_multiple_boards():
    """Test that the singular function gets upset if there are multiple boards."""
    board_group = BoardGroup(TestingBoard, TwoBoardsTestingBackend())

    with pytest.raises(Exception):
        board_group.singular()


def test_board_group_boards():
    """Test that the boards property works on a board group."""
    board_group = BoardGroup(TestingBoard, OneBoardTestingBackend())

    assert len(board_group.boards) == 1
    assert type(board_group.boards[f"SERIAL {id(testing_board_instance_one)}"]) == TestingBoard  # noqa: E501


def test_board_group_boards_multiple():
    """Test that the boards property works on multiple boards."""
    board_group = BoardGroup(TestingBoard, TwoBoardsTestingBackend())

    assert len(board_group.boards) == 2
    assert type(board_group.boards[f"SERIAL {id(testing_board_instance_one)}"]) == TestingBoard  # noqa: E501


def test_board_group_boards_zero():
    """Test that the boards property works with no boards."""
    board_group = BoardGroup(TestingBoard, NoBoardTestingBackend())

    assert len(board_group.boards) == 0

    with pytest.raises(KeyError):
        board_group.boards[f"SERIAL {id(testing_board_instance_one)}"]


def test_board_group_board_by_serial():
    """Test that the boards property works with serial indices."""
    board_group = BoardGroup(TestingBoard, OneBoardTestingBackend())

    assert type(board_group[f"SERIAL {id(testing_board_instance_one)}"]) == TestingBoard


def test_board_group_board_by_unknown():
    """Test that the boards property throws an exception with unknown indices."""
    board_group = BoardGroup(TestingBoard, OneBoardTestingBackend())

    with pytest.raises(KeyError):
        board_group[0]

    with pytest.raises(KeyError):
        board_group[""]

    with pytest.raises(KeyError):
        board_group[{}]

    with pytest.raises(KeyError):
        board_group["ARGHHHJ"]


def test_board_group_length():
    """Test that the length operator works on a board group."""
    board_group = BoardGroup(TestingBoard, OneBoardTestingBackend())

    assert len(board_group) == 1


def test_board_group_length_multiple():
    """Test that the length operator works on multiple boards."""
    board_group = BoardGroup(TestingBoard, TwoBoardsTestingBackend())

    assert len(board_group) == 2


def test_board_group_length_zero():
    """Test that the length operator works with no boards."""
    board_group = BoardGroup(TestingBoard, NoBoardTestingBackend())

    assert len(board_group) == 0


def test_board_group_iteration():
    """Test that we can iterate over a BoardGroup."""
    board_group = BoardGroup(TestingBoard, TwoBoardsTestingBackend())

    count = 0

    for b in board_group:
        assert type(b) == TestingBoard
        count += 1

    assert count == 2
