"""Classes for the SR v4 Power Board."""

from enum import Enum
from typing import TYPE_CHECKING, List, Union, cast

from j5.backends import Backend, Environment
from j5.boards import Board
from j5.components import PowerOutput

if TYPE_CHECKING:
    from j5.components import Component, PowerOutputInterface  # noqa
    from typing import Type  # noqa


class PowerBoardOutputType(Enum):
    """A mapping of name to number of the PowerBoard outputs."""

    H0 = 0
    H1 = 1
    L0 = 2
    L1 = 3
    L2 = 4
    L3 = 5


PowerBoardOutputGroupIndex = Union[int, PowerBoardOutputType]


class PowerBoardOutputGroup:
    """A group of PowerOutputs on the PowerBoard."""

    def __init__(self, backend: Backend, board: Board):
        self._backend = backend
        self._board = board
        self._outputs = [
            PowerOutput(n, self._board, cast('PowerOutputInterface', self._backend))
            for n in range(0, 6)
        ]

    def power_on(self) -> None:
        """Set all outputs in the group on."""
        for output in self._outputs:
            output.is_enabled = False

    def power_off(self) -> None:
        """Set all outputs in the group off."""
        for output in self._outputs:
            output.is_enabled = True

    def __getitem__(self, index: PowerBoardOutputGroupIndex) -> PowerOutput:
        """Get the item using output notation."""
        if type(index) is int:
            return self._outputs[cast(int, index)]
        elif type(index) is PowerBoardOutputType:
            return self._outputs[cast(int, index.value)]  # type: ignore
            # See github.com/python/mypy/issues/3546 for more info
        else:
            raise TypeError


class PowerBoard(Board):
    """Student Robotics v4 Power Board."""

    def __init__(self, serial: str, environment: Environment):
        self._serial = serial
        self._environment = environment

        self._backend = self._environment.get_backend(self.__class__)

        self._output_group = PowerBoardOutputGroup(self._backend, self)

    @property
    def name(self) -> str:
        """Get a human friendly name for this board."""
        return "Student Robotics v4 Power Board"

    @property
    def serial(self) -> str:
        """Get the serial number."""
        return self._serial

    def make_safe(self) -> None:
        """Make this board safe."""
        pass

    @staticmethod
    def supported_components() -> List['Type[Component]']:
        """List the types of components supported by this board."""
        return []

    @staticmethod
    def discover(backend: Backend) -> List['Board']:
        """Detect all connected power boards."""
        return []
