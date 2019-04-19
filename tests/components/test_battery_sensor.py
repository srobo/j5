"""Tests for the Battery Sensor Classes."""

from j5.components.battery_sensor import BatterySensor, BatterySensorInterface


class MockBatterySensorDriver(BatterySensorInterface):
    """A testing driver for the led."""

    def get_battery_sensor_voltage(self, identifier: int) -> float:
        """Get the voltage of a battery sensor."""
        return 5.0

    def get_battery_sensor_current(self, identifier: int) -> float:
        """Get the current of a battery sensor."""
        return 2.0


def test_battery_sensor_interface_implementation() -> None:
    """Test that we can implement the BatterySensorInterface."""
    MockBatterySensorDriver()


def test_battery_sensor_instantiation() -> None:
    """Test that we can instantiate a BatterySensor."""
    BatterySensor(0, MockBatterySensorDriver())


def test_battery_sensor_interface_class() -> None:
    """Test that the interface class is correct."""
    assert BatterySensor.interface_class() is BatterySensorInterface


def test_battery_sensor_voltage() -> None:
    """Test that we can get the voltage of a battery sensor."""
    battery = BatterySensor(0, MockBatterySensorDriver())
    assert type(battery.voltage) is float
    assert battery.voltage == 5.0


def test_battery_sensor_current() -> None:
    """Test that we can get the current of a battery sensor."""
    battery = BatterySensor(0, MockBatterySensorDriver())
    assert type(battery.current) is float
    assert battery.current == 2.0
