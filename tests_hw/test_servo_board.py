"""Test the SR v4 Power Board."""

from datetime import timedelta
from time import sleep

from j5 import BaseRobot, BoardGroup
from j5.backends.hardware.sr.v4 import (
    SRV4PowerBoardHardwareBackend,
    SRV4ServoBoardHardwareBackend,
)
from j5.boards.sr.v4 import PowerBoard, ServoBoard
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
        sleep(0.2)  # Give time for servo board to initialise.

        self.servo_boards = BoardGroup.get_board_group(
            ServoBoard,
            SRV4ServoBoardHardwareBackend,
        )
        self.servo_board: ServoBoard = self.servo_boards.singular()


if __name__ == "__main__":
    print("Testing SR v4 Servo Board.")

    r = Robot()

    r.power_board.piezo.buzz(timedelta(seconds=0.1), Note.A6)

    print("Waiting for start button...")
    r.power_board.wait_for_start_flash()

    print(f"Serial Number: {r.servo_board.serial_number}")
    print(f"Firmware version: {r.servo_board.firmware_version}")

    for servo in r.servo_board.servos:
        print(f"Set servo {servo.identifier} to 1")
        servo.position = 1
        sleep(0.1)

    for servo in r.servo_board.servos:
        print(f"Set servo {servo.identifier} to 0")
        servo.position = 0
        sleep(0.1)

    for servo in r.servo_board.servos:
        print(f"Set servo {servo.identifier} to -1")
        servo.position = -1
        sleep(0.1)
