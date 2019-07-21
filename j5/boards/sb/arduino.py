"""Classes for the SourceBots Arduino."""
from enum import IntEnum
from typing import Mapping, Optional, Set, Type, Union, cast

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


class AnaloguePin(IntEnum):
    """Analogue Pins numbering."""

    A0 = 14
    A1 = 15
    A2 = 16
    A3 = 17
    A4 = 18
    A5 = 19


PinNumber = Union[int, AnaloguePin]


class SBArduinoBoard(Board):
    """SourceBots Arduino Board."""

    _led: LED
    _digital_pins: Mapping[int, GPIOPin]
    _analogue_pins: Mapping[AnaloguePin, GPIOPin]
    name: str = "Arduino Uno"

    def __init__(self, serial: str, backend: Backend):
        self._serial = serial
        self._backend = backend

        self._led = LED(0, cast(LEDInterface, self._backend))

        # Digital Pins
        # Note that pins 0 and 1 are used for serial comms.
        self._digital_pins = {
            i: GPIOPin(
                i,
                cast(GPIOPinInterface, self._backend),
                initial_mode=GPIOPinMode.DIGITAL_INPUT,
                hardware_modes={
                    GPIOPinMode.DIGITAL_INPUT,
                    GPIOPinMode.DIGITAL_INPUT_PULLUP,
                    GPIOPinMode.DIGITAL_OUTPUT,
                },
            )
            for i in range(2, 14)
        }

        self._analogue_pins = {
            i: GPIOPin(
                i,
                cast(GPIOPinInterface, self._backend),
                initial_mode=GPIOPinMode.ANALOGUE_INPUT,
                hardware_modes={
                    GPIOPinMode.ANALOGUE_INPUT,
                    GPIOPinMode.DIGITAL_INPUT,
                    GPIOPinMode.DIGITAL_INPUT_PULLUP,
                    GPIOPinMode.DIGITAL_OUTPUT,
                },
            )
            for i in AnaloguePin
        }

    @property
    def serial(self) -> str:
        """Get the serial number."""
        return self._serial

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of the board."""
        return self._backend.firmware_version

    @property
    def pins(self) -> Mapping[PinNumber, GPIOPin]:
        """Get the GPIO pins."""
        pins: Mapping[PinNumber, GPIOPin] = {
            **cast(Mapping[PinNumber, GPIOPin], self._analogue_pins),
            **cast(Mapping[PinNumber, GPIOPin], self._digital_pins),

        }
        return pins

    def make_safe(self) -> None:
        """Make this board safe."""
        pass

    @staticmethod
    def supported_components() -> Set[Type[Component]]:
        """List the types of components supported by this board."""
        return {
            GPIOPin,
            LED,
        }
