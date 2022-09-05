"""Classes for the SR v4 Power Board."""

from enum import Enum
from time import sleep
from typing import TYPE_CHECKING, Mapping, Optional, Set, Type, cast

from j5.backends import Backend
from j5.boards import Board
from j5.components import (
    LED,
    BatterySensor,
    Button,
    Component,
    Piezo,
    PowerOutput,
    PowerOutputGroup,
)

if TYPE_CHECKING:  # pragma: no cover
    from j5.components import (  # noqa: F401
        BatterySensorInterface,
        ButtonInterface,
        LEDInterface,
        PiezoInterface,
        PowerOutputInterface,
    )


class PowerOutputPosition(Enum):
    """
    A mapping of name to number of the PowerBoard outputs.

    The numbers here are the same as used in wire communication with the PowerBoard.
    """

    H0 = 0
    H1 = 1
    L0 = 2
    L1 = 3
    L2 = 4
    L3 = 5
    FIVE_VOLT = 6


class PowerBoard(Board):
    """Student Robotics v4 Power Board."""

    name: str = "Student Robotics v4 Power Board"

    class AvailableFeatures(Board.AvailableFeatures):
        """Features available on the board."""

        BRAIN_OUTPUT = "brain_output"  # Brain is powered from L2
        REG_5V_CONTROL = "5v_control"  # 5V output is controllable

    def __init__(self, serial: str, backend: Backend):
        self._serial = serial
        self._backend = backend

        self._outputs: Mapping[PowerOutputPosition, PowerOutput] = {
            output: PowerOutput(
                output.value, cast("PowerOutputInterface", self._backend),
            )
            for output in PowerOutputPosition
            if self._output_is_controllable(self.features, output)
        }

        self._output_group = PowerOutputGroup(self._outputs)

        self._piezo = Piezo(0, cast("PiezoInterface", self._backend))
        self._start_button = Button(0, cast("ButtonInterface", self._backend))
        self._battery_sensor = BatterySensor(
            0, cast("BatterySensorInterface", self._backend),
        )

        self._run_led = LED(0, cast("LEDInterface", self._backend))
        self._error_led = LED(1, cast("LEDInterface", self._backend))

    @staticmethod
    def _output_is_controllable(
        features: Set['Board.AvailableFeatures'],
        output: PowerOutputPosition,
    ) -> bool:
        """
        Determine whether we should be controlling an output.

        :param features: The features available on the backend.
        :param output: The output to check
        :returns: True if we can control the output.
        """
        if PowerBoard.AvailableFeatures.BRAIN_OUTPUT in features and \
           output is PowerOutputPosition.L2:
            return False

        if PowerBoard.AvailableFeatures.REG_5V_CONTROL not in features and \
           output is PowerOutputPosition.FIVE_VOLT:
            return False

        return True

    @property
    def serial_number(self) -> str:
        """
        Get the serial number of the board.

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
    def outputs(self) -> PowerOutputGroup:
        """
        Get the power outputs.

        :returns: Group of power outputs attached to the board.
        """
        return self._output_group

    @property
    def piezo(self) -> Piezo:
        """
        Get the piezo sounder.

        :returns: Piezo object attached to the board.
        """
        return self._piezo

    @property
    def start_button(self) -> Button:
        """
        Get the start button.

        :returns: Start button attached to the board.
        """
        return self._start_button

    @property
    def battery_sensor(self) -> BatterySensor:
        """
        Get the battery sensor.

        :returns: Battery sensor attached to the board.
        """
        return self._battery_sensor

    def make_safe(self) -> None:
        """Make this board safe."""
        self._output_group.power_off()

    def wait_for_start_flash(self) -> None:
        """
        Wait for the start button to be pressed and flash.

        The LED will remain on once the start button has been pressed.
        """
        counter = 0
        led_state = False
        while not self.start_button.is_pressed:
            if counter % 6 == 0:
                led_state = not led_state
                self._run_led.state = led_state
            sleep(0.05)
            counter += 1

        # Turn on the LED now the button has been pressed.
        self._run_led.state = True

    @staticmethod
    def supported_components() -> Set[Type[Component]]:
        """
        List the types of components supported by this board.

        :returns: Set of components supported by the board.
        """
        return {PowerOutput, Piezo, Button, BatterySensor, LED}
