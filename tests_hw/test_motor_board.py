"""Test the SR v4 Power Board."""

from datetime import timedelta
from time import sleep

from j5 import BaseRobot, BoardGroup
from j5.backends.hardware.sr.v4 import (
    SRV4MotorBoardHardwareBackend,
    SRV4PowerBoardHardwareBackend,
)
from j5.boards.sr.v4 import MotorBoard, PowerBoard
from j5.components.motor import MotorSpecialState
from j5.components.piezo import Note


class Robot(BaseRobot):
    """A basic robot with a power board."""

    def __init__(self) -> None:
        self.power_boards = BoardGroup.get_board_group(
            PowerBoard,
            SRV4PowerBoardHardwareBackend,
        )
        self.power_board: PowerBoard = self.power_boards.singular()

        self.power_board.outputs.power_on()
        sleep(0.2)  # Give time for motor board to initialise.

        self.motor_boards = BoardGroup.get_board_group(
            MotorBoard,
            SRV4MotorBoardHardwareBackend,
        )
        self.motor_board: MotorBoard = self.motor_boards.singular()


if __name__ == "__main__":
    print("Testing SR v4 MotorBoard.")

    r = Robot()

    r.power_board.piezo.buzz(timedelta(seconds=0.1), Note.A6)

    print("Waiting for start button...")
    r.power_board.wait_for_start_flash()

    print(f"Serial number: {r.motor_board.serial_number}")
    print(f"Firmware version: {r.motor_board.firmware_version}")

    for m in r.motor_board.motors:
        print(f"Testing output {m.identifier}")
        for v in range(-10, 10):
            m.power = v / 10
            sleep(0.1)
        m.power = MotorSpecialState.BRAKE
