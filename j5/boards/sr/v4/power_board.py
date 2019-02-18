"""Classes for the SR v4 Power Board."""

from enum import Enum
from typing import TYPE_CHECKING, List, Union, cast, Mapping

from j5.backends import Backend, Environment
from j5.boards import Board
from j5.components import LED, BatterySensor, Button, Piezo, PowerOutput

if TYPE_CHECKING:
    from j5.components import (  # noqa: F401
        Component,
        ButtonInterface,
        PowerOutputInterface,
        PiezoInterface,
        BatterySensorInterface,
        LEDInterface,
    )
    from typing import Type  # noqa: F401


class PowerOutputPosition(Enum):
    """A mapping of name to number of the PowerBoard outputs."""

    H0 = 0
    H1 = 1
    L0 = 2
    L1 = 3
    L2 = 4
    L3 = 5


class PowerOutputGroup:
    """A group of PowerOutputs on the PowerBoard."""

    def __init__(self, backend: Backend, board: Board):
        self._backend = backend
        self._board = board

        self._outputs: Mapping[PowerOutputPosition, PowerOutput] = {
            output: PowerOutput(output.value, self._board, cast("PowerOutputInterface", self._backend))
            for output in PowerOutputPosition
            # Note that in Python 3, Enums are ordered.
        }

    def power_on(self) -> None:
        """Enable all outputs in the group."""
        for output in self._outputs:
            output.is_enabled = True

    def power_off(self) -> None:
        """Disable all outputs in the group."""
        for output in self._outputs:
            output.is_enabled = False

    def __getitem__(self, index: PowerOutputPosition) -> PowerOutput:
        """Get an output using list notation."""
        return self._outputs[index]

    def __len__(self) -> int:
        """Get the number of outputs in the group."""
        return len(self._outputs)


class PowerBoard(Board):
    """Student Robotics v4 Power Board."""

    def __init__(self, serial: str, environment: Environment):
        self._serial = serial
        self._environment = environment

        self._backend = self._environment.get_backend(self.__class__)

        self._output_group = PowerOutputGroup(self._backend, self)
        self._piezo = Piezo(0, self, cast("PiezoInterface", self._backend))
        self._start_button = Button(0, self, cast("ButtonInterface", self._backend))
        self._battery_sensor = BatterySensor(
            0, self, cast("BatterySensorInterface", self._backend),
        )

        self._run_led = LED(0, self, cast("LEDInterface", self._backend))
        self._error_led = LED(0, self, cast("LEDInterface", self._backend))

    @property
    def name(self) -> str:
        """Get a human friendly name for this board."""
        return "Student Robotics v4 Power Board"

    @property
    def serial(self) -> str:
        """Get the serial number."""
        return self._serial

    @property
    def outputs(self) -> PowerOutputGroup:
        """Get the power outputs."""
        return self._output_group

    @property
    def piezo(self) -> Piezo:
        """Get the piezo sounder."""
        return self._piezo

    @property
    def start_button(self) -> Button:
        """Get the start button."""
        return self._start_button

    @property
    def battery_sensor(self) -> BatterySensor:
        """Get the battery sensor."""
        return self._battery_sensor

    def make_safe(self) -> None:
        """Make this board safe."""
        self._output_group.power_off()

    @staticmethod
    def supported_components() -> List["Type[Component]"]:
        """List the types of components supported by this board."""
        return [PowerOutput, Piezo, Button, BatterySensor, LED]

    @staticmethod
    def discover(backend: Backend) -> List["Board"]:
        """Detect all connected power boards."""
        return []
