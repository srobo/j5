"""Test the demo board."""
from typing import Mapping

from j5.backends import Backend, BackendGroup
from j5.boards import Board
from j5.boards.j5 import DemoBoard
from j5.components import LED, LEDInterface


class TestDemoBoardBackend(LEDInterface, Backend):
    """A test backend for the DemoBoard."""

    def set_led_state(self, board: Board, identifier: int, state: bool) -> None:
        """Set the LED state."""
        pass

    def get_led_state(self, board: Board, identifier: int) -> bool:
        """Get the current state of an LED."""
        return True


class TestBackendGroup(BackendGroup):
    """A test backend group."""

    @property
    def supported_boards(self) -> Mapping[Board, Backend]:
        """The supported boards for this backend group."""
        return {DemoBoard: TestDemoBoardBackend}  # type: ignore


def test_demo_board_instantiation():
    """Test that we can instantiate a demo board."""
    demo_board = DemoBoard("00000", TestBackendGroup())

    assert type(demo_board) == DemoBoard


def test_demo_board_name():
    """Test that we can get the name of a demo board."""
    demo_board = DemoBoard("00000", TestBackendGroup())

    assert demo_board.name == "Demo Board"


def test_demo_board_serial():
    """Test that we can get the serial of a demo board."""
    demo_board = DemoBoard("00000", TestBackendGroup())

    assert demo_board.serial == "00000"


def test_demo_board_leds():
    """Test that we can get the leds on a demo board."""
    demo_board = DemoBoard("00000", TestBackendGroup())

    assert len(demo_board.leds) == 3
    assert type(demo_board.leds[0]) == LED


def test_demo_board_led_operation():
    """Test that we can operate the leds on the demo board."""
    demo_board = DemoBoard("00000", TestBackendGroup())

    for led in demo_board.leds:
        led.state = True
        assert led.state


def test_demo_board_detection():
    """Test that we can detect all the demo boards."""
    boards = DemoBoard.detect_all(TestBackendGroup())
    assert len(boards) == 3
