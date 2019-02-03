"""A base class for robots."""

import atexit

from j5.boards import Board


class BaseRobot:
    """A base robot."""

    def make_self(self):
        """Make this robot safe."""
        BaseRobot.make_all_safe()

    @staticmethod
    @atexit.register
    def make_all_safe():
        """Make all boards safe."""
        for board in Board.BOARDS:
            board.make_safe()
