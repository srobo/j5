"""Classes for the SourceBots Arduino."""
from typing import Set, Tuple, Type, cast

from j5.backends import Backend
from j5.boards.arduino.uno import ArduinoUno
from j5.components import LED, Component, DerivedComponent, GPIOPin
from j5.components.derived import UltrasoundInterface, UltrasoundSensor


class SBArduinoBoard(ArduinoUno):
    """SourceBots Arduino Board."""

    FIRMWARE_MODES: Set[Type[DerivedComponent]] = {UltrasoundSensor}

    def __init__(
            self,
            serial: str,
            backend: Backend,
    ):
        super().__init__(serial, backend)

        for pin in self._digital_pins.values():
            pin.firmware_modes = SBArduinoBoard.FIRMWARE_MODES

        self.ultrasound_sensors = UltrasoundSensors(self)

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

    def __getitem__(
        self,
        key: Tuple[ArduinoUno.PinNumber, ArduinoUno.PinNumber],
    ) -> UltrasoundSensor:
        """Get an ultrasound sensor with the given pin configuration."""
        trigger_pin, echo_pin = key
        return UltrasoundSensor(
            gpio_trigger=self._arduino.pins[trigger_pin],
            gpio_echo=self._arduino.pins[echo_pin],
            backend=cast(UltrasoundInterface, self._arduino._backend),
        )
