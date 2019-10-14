"""Test the SourceBots Arduino."""

from time import sleep

from j5 import BaseRobot, BoardGroup
from j5.backends.hardware.sb.arduino import SBArduinoHardwareBackend
from j5.boards.sb.arduino import SBArduinoBoard
from j5.components.gpio_pin import GPIOPinMode


class Robot(BaseRobot):
    """A basic robot with a power board."""

    def __init__(self) -> None:
        self.arduinos = BoardGroup.get_board_group(
            SBArduinoBoard,
            SBArduinoHardwareBackend,
        )
        self.arduino: SBArduinoBoard = self.arduinos.singular()


if __name__ == '__main__':

    print("Testing SR Arduino.")

    r = Robot()

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
