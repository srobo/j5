"""Test the SR v4 Power Board."""

from datetime import timedelta
from time import sleep

import j5.backends.hardware.sr.v4  # noqa: F401
from j5 import BaseRobot, BoardGroup
from j5.backends.hardware import HardwareEnvironment
from j5.boards.sr.v4 import PowerBoard, ServoBoard
from j5.components.piezo import Note


class Robot(BaseRobot):
    """A basic robot with a power board."""

    def __init__(self):
        self.power_boards = BoardGroup(
            PowerBoard,
            HardwareEnvironment.get_backend(PowerBoard),
        )
        self.power_board: PowerBoard = self.power_boards.singular()

        self.power_board.outputs.power_on()

        self.servo_boards = BoardGroup(
            ServoBoard,
            HardwareEnvironment.get_backend(ServoBoard),
        )

        self.servo_board: ServoBoard = self.servo_boards.singular()


if __name__ == '__main__':

    print("Testing SR v4 Servo Board.")

    r = Robot()

    r.power_board.piezo.buzz(timedelta(seconds=0.1), Note.A6)

    print("Waiting for start button...")
    r.power_board.wait_for_start_flash()

    print(f"Serial Number: {r.servo_board.serial}")
    print(f"Firmware version: {r.servo_board.firmware_version}")

    for servo in r.servo_board.servos:
        print(f"Set servo {servo._identifier} to 1")
        servo.position = 1
        sleep(0.1)

    for servo in r.servo_board.servos:
        print(f"Set servo {servo._identifier} to 0")
        servo.position = -1
        sleep(0.1)

    for servo in r.servo_board.servos:
        print(f"Set servo {servo._identifier} to -1")
        servo.position = -1
        sleep(0.1)