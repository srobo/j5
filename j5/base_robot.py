"""A base class for robots."""

from j5.boards import Board


class BaseRobot:
    """A base robot."""

    def make_safe(self) -> None:
        """Make this robot safe."""
        Board.make_all_safe()
