"""Test the Student Robotics Ruggeduino."""

import logging
from time import sleep

from j5 import BaseRobot, BoardGroup
from j5.backends.hardware.sr.v4.ruggeduino import SRV4RuggeduinoHardwareBackend
from j5.boards.sr.v4.ruggeduino import Ruggeduino
from j5.components.gpio_pin import GPIOPinMode

LOGGER = logging.Logger(__name__)

LOGGER.setLevel(logging.DEBUG)


class Robot(BaseRobot):
    """A basic robot with a Ruggeduino."""

    def __init__(self) -> None:
        self.arduinos = BoardGroup.get_board_group(
            Ruggeduino,
            SRV4RuggeduinoHardwareBackend,
        )
        self.arduino: Ruggeduino = self.arduinos.singular()


if __name__ == "__main__":
    print("Testing SR Ruggeduino.")

    r = Robot()

    print(f"Serial number: {r.arduino.serial_number}")
    print(f"Firmware version: {r.arduino.firmware_version}")

    print("Setting all pins high.")
    for pin in range(2, 14):
        r.arduino.pins[pin].mode = GPIOPinMode.DIGITAL_OUTPUT
        r.arduino.pins[pin].digital_write(True)

    sleep(1)

    print("Setting all pins low.")
    for pin in range(2, 14):
        r.arduino.pins[pin].mode = GPIOPinMode.DIGITAL_OUTPUT
        r.arduino.pins[pin].digital_write(False)

    sleep(1)

    for pin in range(2, 14):
        r.arduino.pins[pin].mode = GPIOPinMode.DIGITAL_INPUT
        print(f"Pin {pin} digital state = {r.arduino.pins[pin].digital_read()}")
    for pin in range(14, 18):
        r.arduino.pins[pin].mode = GPIOPinMode.ANALOGUE_INPUT
        print(f"Pin {pin} analogue voltage = {r.arduino.pins[pin].analogue_read()}")

    res = r.arduino.command("q")
    print(res)
