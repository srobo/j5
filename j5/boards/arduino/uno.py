"""
Base classes for Arduino Unos.

This is to avoid duplicating code that is common between different Arduino boards.
"""
from enum import IntEnum
from typing import Iterable, Mapping, Optional, Set, Type, Union, cast

from j5.backends import Backend
from j5.boards import Board
from j5.components import (
    LED,
    Component,
    GPIOPin,
    GPIOPinInterface,
    GPIOPinMode,
    LEDInterface,
)
from j5.components.gpio_pin import FirmwareMode, PinMode
from j5.types import ImmutableDict


class ArduinoUno(Board):
    """Arduino Uno."""

    class AnaloguePin(IntEnum):
        """Analogue Pins numbering."""

        A0 = 14
        A1 = 15
        A2 = 16
        A3 = 17
        A4 = 18
        A5 = 19

    PinNumber = Union[int, AnaloguePin]
    FIRST_ANALOGUE_PIN: PinNumber = AnaloguePin.A0

    _digital_pins: Mapping[int, GPIOPin]
    _analogue_pins: Mapping[AnaloguePin, GPIOPin]

    name: str = "Arduino Uno"

    def __init__(
            self,
            serial: str,
            backend: Backend,
    ):
        self._serial = serial
        self._backend = backend

        self.led = LED(0, cast(LEDInterface, self._backend))

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

        self._analogue_pins = cast(
            Mapping[ArduinoUno.AnaloguePin, GPIOPin],

            self._generate_gpio_pins(
                ArduinoUno.AnaloguePin.__members__.values(),
                initial_mode=GPIOPinMode.ANALOGUE_INPUT,
                hardware_modes={
                    GPIOPinMode.ANALOGUE_INPUT,
                    GPIOPinMode.DIGITAL_INPUT,
                    GPIOPinMode.DIGITAL_INPUT_PULLUP,
                    GPIOPinMode.DIGITAL_OUTPUT,
                },
            ),
        )

    def _generate_gpio_pins(
            self,
            numbering: Iterable[PinNumber],
            initial_mode: PinMode,
            *,
            hardware_modes: Set[GPIOPinMode] = GPIOPin.DEFAULT_HW_MODE,
            firmware_modes: Set[FirmwareMode] = GPIOPin.DEFAULT_FW_MODE,
    ) -> Mapping[PinNumber, GPIOPin]:
        """
        Generate a dict of GPIOPins with the same properties.

        :param numbering: The pin numbers to use for the generated pins.
        :param initial_mode: Initial mode of the generated pins.
        :param hardware_modes: Set of hardware modes supported by the pins.
        :param firmware_modes: Set of firmware modes supported by the pins.
        :returns: Dictionary of generated pins.
        """
        return {
            i: GPIOPin(
                i,
                cast(GPIOPinInterface, self._backend),
                initial_mode=initial_mode,
                hardware_modes=hardware_modes,
                firmware_modes=firmware_modes,
            )
            for i in numbering
        }

    @property
    def serial_number(self) -> str:
        """
        Get the serial number.

        :returns: Serial number of the board.
        """
        return self._serial

    @property
    def firmware_version(self) -> Optional[str]:
        """
        Get the firmware version of the board.

        :returns: Firmware version of the board.
        """
        return self._backend.firmware_version

    @property
    def pins(self) -> ImmutableDict[PinNumber, GPIOPin]:
        """
        Get the GPIO pins.

        :returns: Dictionary of pins on the Arduino.
        """
        pins = ImmutableDict[ArduinoUno.PinNumber, GPIOPin]({
            **cast(Mapping[ArduinoUno.PinNumber, GPIOPin], self._analogue_pins),
            **cast(Mapping[ArduinoUno.PinNumber, GPIOPin], self._digital_pins),

        })
        return pins

    def make_safe(self) -> None:
        """Make this board safe."""

    @staticmethod
    def supported_components() -> Set[Type[Component]]:
        """
        List the types of components supported by this board.

        :returns: Set of components supported by the board.
        """
        return {
            GPIOPin,
            LED,
        }
