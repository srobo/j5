"""Classes for the SourceBots Arduino."""
from enum import IntEnum
from typing import Mapping, Optional, Set, Tuple, Type, Union, cast

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
from j5.components.derived import UltrasoundInterface, UltrasoundSensor


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
                firmware_modes={UltrasoundSensor},
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

        self.ultrasound_sensors = UltrasoundSensors(self)

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
            UltrasoundSensor,
        }


class UltrasoundSensors:
    """
    Helper class for constructing UltrasoundSensor objects on the fly.

    This exists so that arduino.ultrasound_sensors can be accessed using square bracket
    notation like a mapping, for consistency with how other types of component are
    accessed.
    """

    def __init__(self, arduino: SBArduinoBoard):
        self._arduino = arduino

    def __getitem__(self, key: Tuple[PinNumber, PinNumber]) -> UltrasoundSensor:
        """Get an ultrasound sensor with the given pin configuration."""
        trigger_pin, echo_pin = key
        return UltrasoundSensor(
            gpio_trigger=self._arduino.pins[trigger_pin],
            gpio_echo=self._arduino.pins[echo_pin],
            backend=cast(UltrasoundInterface, self._arduino._backend),
        )
