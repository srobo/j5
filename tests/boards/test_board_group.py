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


class TestBoardGroup:
    """Test the board group class."""

    @pytest.fixture
    def empty_board_group(self) -> BoardGroup[MockBoard, NoBoardMockBackend]:
        """An empty board group."""
        return BoardGroup.get_board_group(MockBoard, NoBoardMockBackend)

    @pytest.fixture
    def board_group(self) -> BoardGroup[MockBoard, OneBoardMockBackend]:
        """A board group with one board."""
        return BoardGroup.get_board_group(MockBoard, OneBoardMockBackend)

    @pytest.fixture
    def multi_board_group(self) -> BoardGroup[MockBoard, TwoBoardsMockBackend]:
        """A board group with multiple boards."""
        return BoardGroup.get_board_group(MockBoard, TwoBoardsMockBackend)

    def test_board_group_update(
        self,
        board_group: BoardGroup[MockBoard, OneBoardMockBackend],
    ) -> None:
        """Test that we can refresh the list of boards."""
        assert len(board_group._boards) == 1
        old_board = list(board_group._boards.values())[0]

        board_group.update_boards()
        assert len(board_group._boards) == 1
        new_board = list(board_group._boards.values())[0]
        assert new_board is not old_board

    def test_board_group_update_removes_old_boards(
        self,
        board_group: BoardGroup[MockBoard, OneBoardMockBackend],
    ) -> None:
        """Test that boards are removed from the board group."""
        assert len(board_group._boards) == 1

        # Type ignored because we're now too strict to allow this!
        board_group._backend_class = NoBoardMockBackend  # type: ignore
        board_group.update_boards()
        assert len(board_group._boards) == 0

    def test_board_group_singular(
        self,
        board_group: BoardGroup[MockBoard, OneBoardMockBackend],
    ) -> None:
        """Test that the singular function works on a board group."""
        assert type(board_group.singular()) == MockBoard

    def test_board_group_str(
        self,
        empty_board_group: BoardGroup[MockBoard, NoBoardMockBackend],
        board_group: BoardGroup[MockBoard, OneBoardMockBackend],
        multi_board_group: BoardGroup[MockBoard, TwoBoardsMockBackend],
    ) -> None:
        """Test that the board group can be represented as a string."""
        assert str(empty_board_group) == "Group of Boards - []"
        assert str(board_group) == "Group of Boards - [Testing Board - TESTSERIAL1]"
        assert str(multi_board_group) == "Group of Boards - [Testing Board - TESTSERIAL1, Testing Board - TESTSERIAL2]"

    def test_board_group_repr(
        self,
        board_group: BoardGroup[MockBoard, OneBoardMockBackend],
    ) -> None:
        """Test the representation of the BoardGroup."""
        assert repr(board_group) == "BoardGroup(backend_class=OneBoardMockBackend)"

    def test_board_group_singular_but_multiple_boards(
        self,
        multi_board_group: BoardGroup[MockBoard, TwoBoardsMockBackend],
    ) -> None:
        """Test that the singular function gets upset if there are multiple boards."""
        with pytest.raises(CommunicationError):
            multi_board_group.singular()

    def test_board_group_singular_but_no_boards(
        self,
        empty_board_group: BoardGroup[MockBoard, NoBoardMockBackend],
    ) -> None:
        """Test that the singular function gets upset if there are no boards."""
        with pytest.raises(CommunicationError):
            empty_board_group.singular()

    def test_board_group_boards(
        self,
        board_group: BoardGroup[MockBoard, OneBoardMockBackend],
    ) -> None:
        """Test that the boards property works on a board group."""
        assert len(board_group._boards) == 1
        assert type(list(board_group._boards.values())[0]) == MockBoard

    def test_board_group_boards_multiple(
        self,
        multi_board_group: BoardGroup[MockBoard, TwoBoardsMockBackend],
    ) -> None:
        """Test that the boards property works on multiple boards."""
        assert len(multi_board_group._boards) == 2
        assert type(list(multi_board_group._boards.values())[0]) == MockBoard

    def test_board_group_boards_zero(
        self,
        empty_board_group: BoardGroup[MockBoard, NoBoardMockBackend],
    ) -> None:
        """Test that the boards property works with no boards."""
        assert len(empty_board_group._boards) == 0

        with pytest.raises(KeyError):
            empty_board_group._boards["SERIAL0"]

    def test_board_group_board_by_serial_number(
        self,
        board_group: BoardGroup[MockBoard, OneBoardMockBackend],
    ) -> None:
        """Test that the boards property works with serial indices."""
        assert isinstance(
            board_group[list(board_group._boards.values())[0].serial_number],
            MockBoard,
        )

    def test_board_group_board_by_unknown(
        self,
        board_group: BoardGroup[MockBoard, OneBoardMockBackend],
    ) -> None:
        """Test that the boards property throws an exception with unknown indices."""
        with pytest.raises(TypeError):
            board_group[0]  # type: ignore

        with pytest.raises(KeyError):
            board_group[""]

        with pytest.raises(TypeError):
            board_group[{}]  # type: ignore

        with pytest.raises(KeyError):
            board_group["ARGHHHJ"]

    def test_board_group_length_zero(
        self,
        empty_board_group: BoardGroup[MockBoard, NoBoardMockBackend],
    ) -> None:
        """Test that the length operator works with no boards."""
        assert len(empty_board_group) == 0

    def test_board_group_length(
        self,
        board_group: BoardGroup[MockBoard, OneBoardMockBackend],
    ) -> None:
        """Test that the length operator works on a board group."""
        assert len(board_group) == 1

    def test_board_group_length_multiple(
        self,
        multi_board_group: BoardGroup[MockBoard, TwoBoardsMockBackend],
    ) -> None:
        """Test that the length operator works on multiple boards."""
        assert len(multi_board_group) == 2

    def test_board_group_get_backend_class(
        self,
        multi_board_group: BoardGroup[MockBoard, TwoBoardsMockBackend],
    ) -> None:
        """Test that the Backend class getter works."""
        assert multi_board_group.backend_class is TwoBoardsMockBackend

    def test_board_group_get_boards(
        self,
        multi_board_group: BoardGroup[MockBoard, TwoBoardsMockBackend],
    ) -> None:
        """Test that the boards list getter works."""
        assert type(multi_board_group.boards) is list
        assert len(multi_board_group.boards) == 2
        assert type(multi_board_group.boards[0]) is MockBoard

    def test_board_group_contains(
        self,
        multi_board_group: BoardGroup[MockBoard, TwoBoardsMockBackend],
    ) -> None:
        """Test that __contains__ behaves as expected."""
        assert "TESTSERIAL1" in multi_board_group
        assert "TESTSERIAL2" in multi_board_group
        assert "TESTSERIAL3" not in multi_board_group

    def test_board_group_iteration(
        self,
        multi_board_group: BoardGroup[MockBoard, TwoBoardsMockBackend],
    ) -> None:
        """Test that we can iterate over a BoardGroup."""
        count = 0

        for b in multi_board_group:
            assert type(b) == MockBoard
            count += 1

        assert count == 2

    def test_board_group_iteration_sorted_by_serial(
        self,
        multi_board_group: BoardGroup[MockBoard, TwoBoardsMockBackend],
    ) -> None:
        """Test that the boards yielded by iterating over a BoardGroup are sorted."""
        serial_numbers = [board.serial_number for board in multi_board_group]
        assert len(serial_numbers) == 2
        assert serial_numbers[0] < serial_numbers[1]

    def test_board_group_simultaneous_iteration(
        self,
        multi_board_group: BoardGroup[MockBoard, TwoBoardsMockBackend],
    ) -> None:
        """Test that iterators returned by iter(BoardGroup) are independent."""
        iter1 = iter(multi_board_group)
        iter2 = iter(multi_board_group)
        assert next(iter1) is multi_board_group["TESTSERIAL1"]
        assert next(iter2) is multi_board_group["TESTSERIAL1"]
        assert next(iter1) is multi_board_group["TESTSERIAL2"]
        assert next(iter2) is multi_board_group["TESTSERIAL2"]

    def test_board_group_make_safe(
        self,
        multi_board_group: BoardGroup[MockBoard, TwoBoardsMockBackend],
    ) -> None:
        """Test that the make_safe function is called on all Boards in a BoardGroup."""
        assert not any(board._safe for board in multi_board_group)
        multi_board_group.make_safe()
        assert all(board._safe for board in multi_board_group)

    def test_board_group_mutability(
        self,
        multi_board_group: BoardGroup[MockBoard, TwoBoardsMockBackend],
    ) -> None:
        """
        Test that the members of BoardGroup are immutable.

        This is to try and ensure that an error would be thrown on a student typo.
        """
        with pytest.raises(TypeError):
            multi_board_group["TESTSERIAL1"] = 12  # type: ignore

    def test_get_by_serial(
        self,
        multi_board_group: BoardGroup[MockBoard, TwoBoardsMockBackend],
    ) -> None:
        """Test that we can get a board by serial."""
        board = multi_board_group["TESTSERIAL1"]
        assert isinstance(board, MockBoard)

    def test_get_by_serial_unavailable_serial(
        self,
        multi_board_group: BoardGroup[MockBoard, TwoBoardsMockBackend],
    ) -> None:
        """Test that we get a KeyError if the serial isn't available."""
        with pytest.raises(KeyError) as e:
            multi_board_group["BEES"]
        assert (
            str(e.value) == "'Could not find a board with the serial number BEES;"
            " Available board serials: TESTSERIAL1, TESTSERIAL2'"
        )

    def test_get_by_serial_empty(
        self,
        empty_board_group: BoardGroup[MockBoard, NoBoardMockBackend],
    ) -> None:
        """Test that we get a KeyError."""
        with pytest.raises(KeyError) as e:
            empty_board_group["TESTSERIAL1"]
        assert str(e.value) == "'There are no MockBoard boards available.'"
