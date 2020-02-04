"""
Base classes for Arduino Unos.

This is to avoid duplicating code that is common between different Arduino boards.
"""
from abc import abstractmethod
from enum import IntEnum
from typing import Union, Mapping, cast, Set, Type

from j5.backends import Backend

from j5.boards import Board
from j5.components import LED, GPIOPin, LEDInterface, GPIOPinInterface, GPIOPinMode, \
    Component


class AnaloguePin(IntEnum):
    """Analogue Pins numbering."""

    A0 = 14
    A1 = 15
    A2 = 16
    A3 = 17
    A4 = 18
    A5 = 19


PinNumber = Union[int, AnaloguePin]


class ArduinoUno(Board):
    """Generic Arduino Uno."""

    _led: LED
    _digital_pins: Mapping[int, GPIOPin]
    _analogue_pins: Mapping[AnaloguePin, GPIOPin]

    def __init__(
            self,
            serial: str,
            backend: Backend,
    ):
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
    def pins(self) -> Mapping[PinNumber, GPIOPin]:
        """Get the GPIO pins."""
        pins: Mapping[PinNumber, GPIOPin] = {
            **cast(Mapping[PinNumber, GPIOPin], self._analogue_pins),
            **cast(Mapping[PinNumber, GPIOPin], self._digital_pins),

        }
        return pins

    @abstractmethod
    def make_safe(self) -> None:
        """Make this board safe."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def supported_components() -> Set[Type[Component]]:
        """List the types of components supported by this board."""
        raise NotImplementedError
