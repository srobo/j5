"""Tests for the power output classes."""
from typing import TYPE_CHECKING, List, Optional, Type

from j5.boards import Board
from j5.components.power_output import PowerOutput, PowerOutputInterface

if TYPE_CHECKING:
    from j5.components import Component  # noqa


class MockPowerOutputDriver(PowerOutputInterface):
    """A testing driver for power outputs."""

    def __init__(self) -> None:
        self._enabled = False

    def get_power_output_enabled(self, identifier: int) -> bool:
        """Get whether a power output is enabled."""
        return self._enabled

    def set_power_output_enabled(
        self, identifier: int, enabled: bool,
    ) -> None:
        """Set whether a power output is enabled."""
        self._enabled = enabled

    def get_power_output_current(self, identifier: int) -> float:
        """Get the current being drawn on a power output, in amperes."""
        return 8.1


class MockPowerOutputBoard(Board):
    """A testing board for the power output."""

    def __init__(self) -> None:
        pass

    @property
    def name(self) -> str:
        """The name of this board."""
        return "Testing Power Output Board"

    @property
    def serial(self) -> str:
        """The serial number of this board."""
        return "SERIAL"

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of this board."""
        return None

    @staticmethod
    def supported_components() -> List[Type["Component"]]:
        """List the types of component that this Board supports."""
        return [PowerOutput]

    def make_safe(self) -> None:
        """Make this board safe."""
        pass


def test_power_output_interface_implementation() -> None:
    """Test that we can implement the PowerOutputInterface."""
    MockPowerOutputDriver()


def test_power_output_instantiation() -> None:
    """Test that we can instantiate a PowerOutput."""
    PowerOutput(0, MockPowerOutputBoard(), MockPowerOutputDriver())


def test_power_output_interface() -> None:
    """Test that the class returns the correct interface."""
    assert PowerOutput.interface_class() is PowerOutputInterface


def test_power_output_enabled() -> None:
    """Test the is_enabled property of a PowerOutput."""
    power_output = PowerOutput(0, MockPowerOutputBoard(), MockPowerOutputDriver())
    assert power_output.is_enabled is False
    power_output.is_enabled = True
    assert power_output.is_enabled is True


def test_power_output_current() -> None:
    """Test the current property of a PowerOutput."""
    power_output = PowerOutput(0, MockPowerOutputBoard(), MockPowerOutputDriver())
    assert type(power_output.current) is float
    assert power_output.current == 8.1
