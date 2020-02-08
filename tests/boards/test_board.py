"""Test the base classes for boards."""
from j5.boards.board import Board

from .utils import (
    MockBoard,
    MockBoardWithConstructor,
    NoBoardMockBackend,
    OneBoardMockBackend,
    TwoBoardsMockBackend,
)


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
