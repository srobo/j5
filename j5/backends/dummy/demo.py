"""Dummy Backends for the demo boards."""

from j5.backends import Backend
from j5.boards import Board
from j5.components import LEDInterface


class DemoBoardDummyBackend(LEDInterface, Backend):
    """The dummy implementation of the DemoBoard."""

    def set_led_state(self, board: Board, identifier: int, state: bool) -> None:
        """Set the state of an LED."""
        print(f"Set LED {str(identifier)} to {str(state)} on {str(board)}")

    def get_led_state(self, board: Board, identifier: int) -> bool:
        """Set the state of an LED."""
        return False
