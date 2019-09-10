"""Test the SourceBots Arduino."""

from datetime import timedelta
from time import sleep

from j5 import BaseRobot, BoardGroup
from j5.backends.hardware.sb.arduino import SBArduinoHardwareBackend
from j5.backends.hardware.sr.v4.power_board import (
    SRV4PowerBoardHardwareBackend,
)
from j5.boards.sb.arduino import SBArduinoBoard
from j5.boards.sr.v4 import PowerBoard
from j5.components.gpio_pin import GPIOPinMode
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
        sleep(0.2)  # Give time for arduino to initialise.

        self.arduinos = BoardGroup.get_board_group(
            SBArduinoBoard,
            SBArduinoHardwareBackend,
        )
        self.arduino: SBArduinoBoard = self.arduinos.singular()


if __name__ == '__main__':

    print("Testing SR Arduino.")

    r = Robot()

    r.power_board.piezo.buzz(timedelta(seconds=0.1), Note.A6)

    print("Waiting for start button...")
    r.power_board.wait_for_start_flash()

    print(f"Serial number: {r.arduino.serial}")
    print(f"Firmware version: {r.arduino.firmware_version}")

    print("Setting all pins high.")
    for pin in range(2, 14):
        r.arduino.pins[pin].mode = GPIOPinMode.DIGITAL_OUTPUT
        r.arduino.pins[pin].digital_state = True

    sleep(1)

    print("Setting all pins low.")
    for pin in range(2, 14):
        r.arduino.pins[pin].mode = GPIOPinMode.DIGITAL_OUTPUT
        r.arduino.pins[pin].digital_state = False

    sleep(1)

    for pin in range(2, 14):
        r.arduino.pins[pin].mode = GPIOPinMode.DIGITAL_INPUT
        print(f"Pin {pin} digital state = {r.arduino.pins[pin].digital_state}")
    for pin in range(14, 18):
        r.arduino.pins[pin].mode = GPIOPinMode.ANALOGUE_INPUT
        print(f"Pin {pin} analogue voltage = {r.arduino.pins[pin].analogue_value}")
