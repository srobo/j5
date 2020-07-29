from j5 import BaseRobot, BoardGroup
from j5.backends.console.sr.v4 import SRV4PowerBoardConsoleBackend
from j5.boards.sr.v4 import PowerBoard


class MyRobot(BaseRobot):
    """A robot with a few boards."""

    def __init__(self) -> None:
        self._power_boards = BoardGroup.get_board_group(
            PowerBoard,
            SRV4PowerBoardConsoleBackend,
        )
        self.power_board = self._power_boards.singular()  # Restrict to exactly one board.

        # Expose just a component to the user.
        self.big_led = self.power_board.outputs[0]


r = MyRobot()

# Ensure all outputs on the power board are off.

for output in r.power_board.outputs:
    output.is_enabled = False

# Turn on the big LED
r.big_led.is_enabled = True
