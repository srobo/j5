from j5 import BaseRobot, BoardGroup
from j5.backends.console.sr.v4 import (
    SRV4MotorBoardConsoleBackend,
    SRV4PowerBoardConsoleBackend,
)
from j5.boards.sr.v4 import MotorBoard, PowerBoard


class MyRobot(BaseRobot):
    """A robot with a few boards."""

    def __init__(self) -> None:
        self._power_boards = BoardGroup.get_board_group(
            PowerBoard,
            SRV4PowerBoardConsoleBackend,
        )
        self.power_board = self._power_boards.singular()  # Restrict to exactly one board.

        self.motor_boards = BoardGroup.get_board_group(
            MotorBoard,
            SRV4MotorBoardConsoleBackend,
        )


r = MyRobot()

print(f"Found Power Board: {r.power_board.serial_number}")
print(f"Power Board Firmware: {r.power_board.firmware_version}")

# Access a board specific function
r.power_board.wait_for_start_flash()

print(f"Found {len(r.motor_boards)} Motor Board(s):")

# Iterate over the boards in a board group
for board in r.motor_boards:
    print(f" - {board.serial_number} - Version {board.firmware_version}")

# Access board by serial number
r.motor_boards["218312"].make_safe()
