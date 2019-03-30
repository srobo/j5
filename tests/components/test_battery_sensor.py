"""Tests for the Battery Sensor Classes."""
from typing import TYPE_CHECKING, List, Optional, Type

from j5.boards import Board
from j5.components.battery_sensor import BatterySensor, BatterySensorInterface

if TYPE_CHECKING:  # pragma: nocover
    from j5.components import Component  # noqa


class MockBatterySensorDriver(BatterySensorInterface):
    """A testing driver for the led."""

    def get_battery_sensor_voltage(self, identifier: int) -> float:
        """Get the voltage of a battery sensor."""
        return 5.0

    def get_battery_sensor_current(self, identifier: int) -> float:
        """Get the current of a battery sensor."""
        return 2.0


class MockBatterySensorBoard(Board):
    """A testing board for the BatterySensor."""

    def __init__(self) -> None:
        pass

    @property
    def name(self) -> str:
        """The name of this board."""
        return "Testing Battery Sensor Board"

    @property
    def serial(self) -> str:
        """The serial number of this board."""
        return "SERIAL"

    @staticmethod
    def supported_components() -> List[Type['Component']]:
        """List the types of component that this Board supports."""
        return [BatterySensor]

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of this board."""
        return None

    def make_safe(self) -> None:
        """Make this board safe."""
        pass


def test_battery_sensor_interface_implementation() -> None:
    """Test that we can implement the BatterySensorInterface."""
    MockBatterySensorDriver()


def test_battery_sensor_instantiation() -> None:
    """Test that we can instantiate a BatterySensor."""
    BatterySensor(0, MockBatterySensorBoard(), MockBatterySensorDriver())


def test_battery_sensor_interface_class() -> None:
    """Test that the interface class is correct."""
    assert BatterySensor.interface_class() is BatterySensorInterface


def test_battery_sensor_voltage() -> None:
    """Test that we can get the voltage of a battery sensor."""
    battery = BatterySensor(0, MockBatterySensorBoard(), MockBatterySensorDriver())
    assert type(battery.voltage) is float
    assert battery.voltage == 5.0


def test_battery_sensor_current() -> None:
    """Test that we can get the current of a battery sensor."""
    battery = BatterySensor(0, MockBatterySensorBoard(), MockBatterySensorDriver())
    assert type(battery.current) is float
    assert battery.current == 2.0
