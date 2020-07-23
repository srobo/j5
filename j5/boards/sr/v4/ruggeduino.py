"""
Classes for the Student Robotics Ruggeduino.

It's similar to the Sourcebots Arduino, but without official ultrasound support.
"""
from typing import Optional, Set, Type, cast

from j5.backends import Backend
from j5.boards.arduino.uno import ArduinoUno
from j5.components import (
    LED,
    Component,
    GPIOPin,
    GPIOPinMode,
    StringCommandComponent,
    StringCommandComponentInterface,
)


class Ruggeduino(ArduinoUno):
    """Student Robotics Ruggeduino board."""

    name: str = "Ruggeduino"

    def __init__(
            self,
            serial: str,
            backend: Backend,
    ):
        super().__init__(serial, backend)

        # Digital Pins
        # Note that pins 0 and 1 are used for serial comms.
        self._digital_pins = self._generate_gpio_pins(
            range(2, ArduinoUno.FIRST_ANALOGUE_PIN),
            initial_mode=GPIOPinMode.DIGITAL_INPUT,
            hardware_modes={
                GPIOPinMode.DIGITAL_INPUT,
                GPIOPinMode.DIGITAL_INPUT_PULLUP,
                GPIOPinMode.DIGITAL_OUTPUT,
            },
        )
        self.command = StringCommandComponent(
            0,
            cast(StringCommandComponentInterface, self._backend),
        )

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of the board."""
        return self._backend.firmware_version

    @staticmethod
    def supported_components() -> Set[Type[Component]]:
        """List the types of components supported by this board."""
        return {
            GPIOPin,
            LED,
            StringCommandComponent,
        }
