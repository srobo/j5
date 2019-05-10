"""Test the SR v4 Power Board."""

from datetime import timedelta
from time import sleep

from j5 import BaseRobot, BoardGroup
from j5.backends.hardware import HardwareEnvironment
from j5.backends.hardware.sr.v4.power_board import (  # noqa: F401
    SRV4PowerBoardHardwareBackend,
)
from j5.boards.sr.v4.power_board import PowerBoard, PowerOutputPosition
from j5.components.piezo import Note


class Robot(BaseRobot):
    """A basic robot with a power board."""

    def __init__(self) -> None:
        self.power_boards = BoardGroup[PowerBoard](
            HardwareEnvironment.get_backend(PowerBoard),
        )
        self.power_board: PowerBoard = self.power_boards.singular()


if __name__ == '__main__':

    print("Testing SR v4 PowerBoard.")

    r = Robot()

    print("Waiting for start button...")
    r.power_board.wait_for_start_flash()

    print(f"Serial number: {r.power_board.serial}")
    print(f"Firmware version: {r.power_board.firmware_version}")

    print(f"Battery voltage: {r.power_board.battery_sensor.voltage} V")
    print(f"Battery current: {r.power_board.battery_sensor.current} A")

    for output in PowerOutputPosition:
        print(f"Output {output} on.")
        r.power_board.outputs[output].is_enabled = True
        sleep(0.5)

    for output in PowerOutputPosition:
        print(f"Output {str(output)} current: {r.power_board.outputs[output].current} A")

    for output in PowerOutputPosition:
        print(f"Output {output} off.")
        r.power_board.outputs[output].is_enabled = False
        sleep(0.5)

    for pitch in Note:
        print(f"Buzzing at pitch: {pitch}")
        r.power_board.piezo.buzz(timedelta(seconds=0.1), pitch)

    for led in [r.power_board._run_led, r.power_board._error_led]:
        print(f"LED {led} is on.")
        led.state = True
        sleep(0.5)
        print(f"LED {led} is off.")
        led.state = False
        sleep(0.5)
