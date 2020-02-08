"""Test Board Group and related classes."""

import pytest

from j5.backends import CommunicationError
from j5.boards.board_group import BoardGroup

from .utils import (
    MockBoard,
    NoBoardMockBackend,
    OneBoardMockBackend,
    TwoBoardsMockBackend,
)


def test_create_boardgroup() -> None:
    """Test that we can create a board group of testing boards."""
    board_group = BoardGroup[MockBoard, NoBoardMockBackend](NoBoardMockBackend)
    assert type(board_group) == BoardGroup


def test_board_group_helper() -> None:
    """Test that the helper function to get the board group works."""
    board_group = BoardGroup.get_board_group(MockBoard, NoBoardMockBackend)
    assert type(board_group) is BoardGroup


def test_board_group_update() -> None:
    """Test that we can refresh the list of boards."""
    board_group = BoardGroup.get_board_group(MockBoard, OneBoardMockBackend)
    assert len(board_group._boards) == 1
    old_board = list(board_group._boards.values())[0]

    board_group.update_boards()
    assert len(board_group._boards) == 1
    new_board = list(board_group._boards.values())[0]
    assert new_board is not old_board


def test_board_group_update_removes_old_boards() -> None:
    """Test that boards that are no longer discovered are removed from the board group."""
    board_group = BoardGroup.get_board_group(MockBoard, OneBoardMockBackend)
    assert len(board_group._boards) == 1

    # Type ignored because we're now too strict to allow this!
    board_group._backend_class = NoBoardMockBackend  # type: ignore
    board_group.update_boards()
    assert len(board_group._boards) == 0


def test_board_group_singular() -> None:
    """Test that the singular function works on a board group."""
    board_group = BoardGroup.get_board_group(MockBoard, OneBoardMockBackend)

    assert type(board_group.singular()) == MockBoard


def test_board_group_str() -> None:
    """Test that the board group can be represented as a string."""
    assert str(BoardGroup.get_board_group(MockBoard, NoBoardMockBackend)) == \
        "Group of Boards - []"
    assert str(BoardGroup.get_board_group(MockBoard, OneBoardMockBackend)) == \
        "Group of Boards - [Testing Board - TESTSERIAL1]"
    assert str(BoardGroup.get_board_group(MockBoard, TwoBoardsMockBackend)) == \
        "Group of Boards - [Testing Board - TESTSERIAL1, Testing Board - TESTSERIAL2]"


def test_board_group_repr() -> None:
    """Test the representation of the BoardGroup."""
    board_group = BoardGroup.get_board_group(MockBoard, NoBoardMockBackend)

    assert repr(board_group) == "BoardGroup(backend_class=NoBoardMockBackend)"


def test_board_group_singular_but_multiple_boards() -> None:
    """Test that the singular function gets upset if there are multiple boards."""
    board_group = BoardGroup.get_board_group(MockBoard, TwoBoardsMockBackend)

    with pytest.raises(CommunicationError):
        board_group.singular()


def test_board_group_singular_but_no_boards() -> None:
    """Test that the singular function gets upset if there are no boards."""
    board_group = BoardGroup.get_board_group(MockBoard, NoBoardMockBackend)

    with pytest.raises(CommunicationError):
        board_group.singular()


def test_board_group_boards() -> None:
    """Test that the boards property works on a board group."""
    board_group = BoardGroup.get_board_group(MockBoard, OneBoardMockBackend)

    assert len(board_group._boards) == 1
    assert type(list(board_group._boards
                .values())[0]) == MockBoard


def test_board_group_boards_multiple() -> None:
    """Test that the boards property works on multiple boards."""
    board_group = BoardGroup.get_board_group(MockBoard, TwoBoardsMockBackend)

    assert len(board_group._boards) == 2
    assert type(list(board_group._boards
                .values())[0]) == MockBoard


def test_board_group_boards_zero() -> None:
    """Test that the boards property works with no boards."""
    board_group = BoardGroup.get_board_group(MockBoard, NoBoardMockBackend)

    assert len(board_group._boards) == 0

    with pytest.raises(KeyError):
        board_group._boards["SERIAL0"]


def test_board_group_board_by_serial() -> None:
    """Test that the boards property works with serial indices."""
    board_group = BoardGroup.get_board_group(MockBoard, OneBoardMockBackend)
    assert type(board_group[list(board_group._boards.values())[0].serial]) == MockBoard


def test_board_group_board_by_unknown() -> None:
    """Test that the boards property throws an exception with unknown indices."""
    board_group = BoardGroup.get_board_group(MockBoard, OneBoardMockBackend)

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
    board_group = BoardGroup.get_board_group(MockBoard, NoBoardMockBackend)

    assert len(board_group) == 0


def test_board_group_length() -> None:
    """Test that the length operator works on a board group."""
    board_group = BoardGroup.get_board_group(MockBoard, OneBoardMockBackend)

    assert len(board_group) == 1


def test_board_group_length_multiple() -> None:
    """Test that the length operator works on multiple boards."""
    board_group = BoardGroup.get_board_group(MockBoard, TwoBoardsMockBackend)

    assert len(board_group) == 2


def test_board_group_get_backend_class() -> None:
    """Test that the Backend class getter works."""
    board_group = BoardGroup.get_board_group(MockBoard, TwoBoardsMockBackend)

    assert board_group.backend_class is TwoBoardsMockBackend


def test_board_group_get_boards() -> None:
    """Test that the boards list getter works."""
    board_group = BoardGroup.get_board_group(MockBoard, TwoBoardsMockBackend)

    assert type(board_group.boards) is list
    assert len(board_group.boards) == 2
    assert type(board_group.boards[0]) is MockBoard


def test_board_group_contains() -> None:
    """Test that __contains__ behaves as expected."""
    board_group = BoardGroup.get_board_group(MockBoard, TwoBoardsMockBackend)
    assert "TESTSERIAL1" in board_group
    assert "TESTSERIAL2" in board_group
    assert "TESTSERIAL3" not in board_group


def test_board_group_iteration() -> None:
    """Test that we can iterate over a BoardGroup."""
    board_group = BoardGroup.get_board_group(MockBoard, TwoBoardsMockBackend)

    count = 0

    for b in board_group:
        assert type(b) == MockBoard
        count += 1

    assert count == 2


def test_board_group_iteration_sorted_by_serial() -> None:
    """Test that the boards yielded by iterating over a BoardGroup are sorted."""
    board_group = BoardGroup.get_board_group(MockBoard, TwoBoardsMockBackend)
    serials = [board.serial for board in board_group]
    assert len(serials) == 2
    assert serials[0] < serials[1]


def test_board_group_simultaneous_iteration() -> None:
    """Test that iterators returned by iter(BoardGroup) are independent."""
    board_group = BoardGroup.get_board_group(MockBoard, TwoBoardsMockBackend)
    iter1 = iter(board_group)
    iter2 = iter(board_group)
    assert next(iter1) is board_group["TESTSERIAL1"]
    assert next(iter2) is board_group["TESTSERIAL1"]
    assert next(iter1) is board_group["TESTSERIAL2"]
    assert next(iter2) is board_group["TESTSERIAL2"]


def test_board_group_make_safe() -> None:
    """Test that the make_safe function is called on all Boards in a BoardGroup."""
    board_group = BoardGroup.get_board_group(MockBoard, TwoBoardsMockBackend)

    assert not any(board._safe for board in board_group)
    board_group.make_safe()
    assert all(board._safe for board in board_group)
