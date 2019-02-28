"""Tests for the Battery Sensor Classes."""
from typing import List, Optional, Type

from j5.backends import Backend
from j5.boards import Board
from j5.components import Component
from j5.components.battery_sensor import BatterySensor, BatterySensorInterface


class MockBatterySensorDriver(BatterySensorInterface):
    """A testing driver for the led."""

    def get_battery_sensor_voltage(self, board: Board, identifier: int) -> float:
        """Get the voltage of a battery sensor."""
        return 5.0

    def get_battery_sensor_current(self, board: Board, identifier: int) -> float:
        """Get the current of a battery sensor."""
        return 2.0


class MockBatterySensorBoard(Board):
    """A testing board for the BatterySensor."""

    @property
    def name(self) -> str:
        """The name of this board."""
        return "Testing Battery Sensor Board"

    @property
    def serial(self) -> str:
        """The serial number of this board."""
        return "SERIAL"

    @property
    def supported_components(self) -> List[Type[Component]]:
        """List the types of component that this Board supports."""
        return [BatterySensor]

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of this board."""
        return self._backend.get_firmware_version(self)

    def make_safe(self) -> None:
        """Make this board safe."""
        pass

    @staticmethod
    def discover(backend: Backend) -> List['MockBatterySensorBoard']:
        """Detect all of the boards on a given backend."""
        return []


def test_battery_sensor_interface_implementation():
    """Test that we can implement the BatterySensorInterface."""
    MockBatterySensorDriver()


def test_battery_sensor_instantiation():
    """Test that we can instantiate a BatterySensor."""
    BatterySensor(0, MockBatterySensorBoard(), MockBatterySensorDriver())


def test_battery_sensor_interface_class():
    """Test that the interface class is correct."""
    assert BatterySensor.interface_class() is BatterySensorInterface


def test_battery_sensor_voltage():
    """Test that we can get the voltage of a battery sensor."""
    battery = BatterySensor(0, MockBatterySensorBoard(), MockBatterySensorDriver())
    assert type(battery.voltage) is float
    assert battery.voltage == 5.0


def test_battery_sensor_current():
    """Test that we can get the current of a battery sensor."""
    battery = BatterySensor(0, MockBatterySensorBoard(), MockBatterySensorDriver())
    assert type(battery.current) is float
    assert battery.current == 2.0
