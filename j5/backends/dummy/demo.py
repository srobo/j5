"""Dummy Backends for the demo boards."""
from typing import List, Optional

from j5.backends import Backend
from j5.backends.dummy.env import DummyEnvironment
from j5.boards import Board
from j5.boards.j5.demo import DemoBoard
from j5.components import LEDInterface


class DemoBoardDummyBackend(LEDInterface, Backend):
    """The dummy implementation of the DemoBoard."""

    environment = DummyEnvironment
    board = DemoBoard

    def set_led_state(self, board: Board, identifier: int, state: bool) -> None:
        """Set the state of an LED."""
        print(f"Set LED {str(identifier)} to {str(state)} on {str(board)}")

    def get_led_state(self, board: Board, identifier: int) -> bool:
        """Get the state of an LED."""
        return False

    def get_firmware_version(self, board: 'Board') -> Optional[str]:
        """Get the firmware version of the board."""
        return None

    @classmethod
    def discover(cls) -> List[Board]:
        """Discover boards available on this backend."""
        return []
