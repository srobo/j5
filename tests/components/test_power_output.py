"""Tests for the power output classes."""
from j5.components.power_output import (
    PowerOutput,
    PowerOutputGroup,
    PowerOutputInterface,
)


class MockPowerOutputDriver(PowerOutputInterface):
    """A testing driver for power outputs."""

    def __init__(self, output_quantity: int = 5) -> None:
        self._enabled = [False for _ in range(0, output_quantity)]

    def get_power_output_enabled(self, identifier: int) -> bool:
        """Get whether a power output is enabled."""
        return self._enabled[identifier]

    def set_power_output_enabled(
        self, identifier: int, enabled: bool,
    ) -> None:
        """Set whether a power output is enabled."""
        self._enabled[identifier] = enabled

    def get_power_output_current(self, identifier: int) -> float:
        """Get the current being drawn on a power output, in amperes."""
        return 8.1


def test_power_output_interface_implementation() -> None:
    """Test that we can implement the PowerOutputInterface."""
    MockPowerOutputDriver()


def test_power_output_instantiation() -> None:
    """Test that we can instantiate a PowerOutput."""
    PowerOutput(0, MockPowerOutputDriver())


def test_power_output_interface() -> None:
    """Test that the class returns the correct interface."""
    assert PowerOutput.interface_class() is PowerOutputInterface


def test_power_output_enabled() -> None:
    """Test the is_enabled property of a PowerOutput."""
    power_output = PowerOutput(0, MockPowerOutputDriver())
    assert power_output.is_enabled is False
    power_output.is_enabled = True
    assert power_output.is_enabled is True


def test_power_output_current() -> None:
    """Test the current property of a PowerOutput."""
    power_output = PowerOutput(0, MockPowerOutputDriver())
    assert type(power_output.current) is float
    assert power_output.current == 8.1


def test_power_output_group_instantiation() -> None:
    """Test that we can instantiate a PowerOutput group."""
    backend = MockPowerOutputDriver(5)
    outputs = {i: PowerOutput(i, backend) for i in range(0, 5)}
    group = PowerOutputGroup(outputs)
    assert type(group) is PowerOutputGroup


def test_power_output_group_power_toggle() -> None:
    """Test that we can toggle a PowerOutputGroup."""
    outputs = {i: PowerOutput(i, MockPowerOutputDriver()) for i in range(0, 5)}
    group = PowerOutputGroup(outputs)

    assert not any(output.is_enabled for output in group)

    group.power_on()
    assert all(output.is_enabled for output in group)

    group.power_off()
    assert not any(output.is_enabled for output in group)


def test_power_output_group_len() -> None:
    """Test the length attribute of PowerOutputGroup."""
    outputs = {i: PowerOutput(i, MockPowerOutputDriver()) for i in range(0, 5)}
    group = PowerOutputGroup(outputs)

    assert len(group) == 5
