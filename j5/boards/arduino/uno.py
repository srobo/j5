"""
Base classes for Arduino Unos.

This is to avoid duplicating code that is common between different Arduino boards.
"""
from abc import abstractmethod
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

    _led: LED
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

        self._led = LED(0, cast(LEDInterface, self._backend))

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
        """Generate a dict of GPIOPins with the same properties."""
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
    def serial(self) -> str:
        """Get the serial number."""
        return self._serial

    @property
    @abstractmethod
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of the board."""
        raise NotImplementedError

    @property
    def pins(self) -> ImmutableDict[PinNumber, GPIOPin]:
        """Get the GPIO pins."""
        pins = ImmutableDict[ArduinoUno.PinNumber, GPIOPin]({
            **cast(Mapping[ArduinoUno.PinNumber, GPIOPin], self._analogue_pins),
            **cast(Mapping[ArduinoUno.PinNumber, GPIOPin], self._digital_pins),

        })
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
