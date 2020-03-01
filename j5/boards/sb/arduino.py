"""Classes for the SourceBots Arduino."""
from typing import Optional, Set, Tuple, Type, cast

from j5.backends import Backend
from j5.boards.j5 import ArduinoUno, PinNumber
from j5.components import LED, Component, GPIOPin
from j5.components.derived import UltrasoundInterface, UltrasoundSensor


class SBArduinoBoard(ArduinoUno):
    """SourceBots Arduino Board."""

    def __init__(
            self,
            serial: str,
            backend: Backend,
    ):
        super().__init__(serial, backend)

        self.ultrasound_sensors = UltrasoundSensors(self)

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of the board."""
        return self._backend.firmware_version

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
