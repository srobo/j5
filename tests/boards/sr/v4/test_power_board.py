"""Tests for the SR v4 Power Board and related classes."""
from datetime import timedelta
from typing import TYPE_CHECKING, Optional, Set

from j5.backends import Backend, Environment
from j5.boards.sr.v4 import PowerBoard, PowerOutputGroup, PowerOutputPosition
from j5.components import (
    LED,
    BatterySensor,
    BatterySensorInterface,
    Button,
    ButtonInterface,
    LEDInterface,
    Piezo,
    PiezoInterface,
    PowerOutput,
    PowerOutputInterface,
    SerialNumberInterface,
)
from j5.components.piezo import Pitch

if TYPE_CHECKING:
    from j5.boards import Board  # noqa


MockEnvironment = Environment("MockEnvironment")


class MockPowerBoardBackend(
    PowerOutputInterface,
    PiezoInterface,
    ButtonInterface,
    BatterySensorInterface,
    LEDInterface,
    SerialNumberInterface,
    Backend,
):
    """A mock power board backend implementation."""

    environment = MockEnvironment
    board = PowerBoard

    @classmethod
    def discover(cls) -> Set["Board"]:
        """Discover the PowerBoards on this backend."""
        return set()

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        return None

    def get_power_output_enabled(self, identifier: int) -> bool:
        """Get the enabled status of a power output."""
        return True

    def set_power_output_enabled(
        self, identifier: int, enabled: bool,
    ) -> None:
        """Set the enabled status of a power output."""
        pass

    def get_power_output_current(self, identifier: int) -> float:
        """Get the current of a power output."""
        return 1.0

    def buzz(
        self, identifier: int, duration: timedelta, pitch: Pitch,
    ) -> None:
        """Buzz the buzzer."""
        pass

    def get_button_state(self, identifier: int) -> bool:
        """Get the state of a button."""
        return True

    def wait_until_button_pressed(self, identifier: int) -> None:
        """Wait until the button is pressed."""
        pass

    def get_battery_sensor_voltage(self, identifier: int) -> float:
        """Get the voltage of a battery sensor."""
        return 11.1

    def get_battery_sensor_current(self, identifier: int) -> float:
        """Get the current of a battery sensor."""
        return 1.0

    def get_led_state(self, identifier: int) -> bool:
        """Get the state of an LED."""
        return True

    def set_led_state(self, identifier: int, state: bool) -> None:
        """Set the state of an LED."""
        pass

    def get_serial_number(self) -> str:
        """Get the serial number."""
        return "SERIAL0"


def test_power_board_instantiation() -> None:
    """Test that we can instantiate a PowerBoard."""
    PowerBoard(MockPowerBoardBackend())


def test_power_board_discover() -> None:
    """Test that we can discover PowerBoards."""
    assert MockPowerBoardBackend.discover() == set()


def test_power_board_name() -> None:
    """Test the name attribute of the PowerBoard."""
    pb = PowerBoard(MockPowerBoardBackend())

    assert pb.name == "Student Robotics v4 Power Board"


def test_power_board_serial() -> None:
    """Test the serial attribute of the PowerBoard."""
    pb = PowerBoard(MockPowerBoardBackend())

    assert pb.serial == "SERIAL0"


def test_firmware_version() -> None:
    """Test the firmware_version attribute of the PowerBoard."""
    pb = PowerBoard(MockPowerBoardBackend())
    assert pb.firmware_version is None


def test_power_board_make_safe() -> None:
    """Test the make_safe method of the PowerBoard."""
    pb = PowerBoard(MockPowerBoardBackend())
    pb.make_safe()


def test_power_board_outputs() -> None:
    """Test the power outputs on the PowerBoard."""
    pb = PowerBoard(MockPowerBoardBackend())

    assert type(pb.outputs) is PowerOutputGroup
    assert len(pb.outputs) == 6

    assert type(pb.outputs[PowerOutputPosition.H0])

    for output in pb.outputs:
        assert type(output) is PowerOutput


def test_power_board_piezo() -> None:
    """Test the Piezo on the PowerBoard."""
    pb = PowerBoard(MockPowerBoardBackend())

    assert type(pb.piezo) is Piezo


def test_power_board_button() -> None:
    """Test the Button on the PowerBoard."""
    pb = PowerBoard(MockPowerBoardBackend())

    assert type(pb.start_button) is Button


def test_power_board_battery_sensor() -> None:
    """Test the Battery Sensor on the Power Board."""
    pb = PowerBoard(MockPowerBoardBackend())

    assert type(pb.battery_sensor) is BatterySensor


def test_power_board_run_led() -> None:
    """Test the run LED on the Power Board."""
    pb = PowerBoard(MockPowerBoardBackend())

    assert type(pb._run_led) is LED


def test_power_board_error_led() -> None:
    """Test the error LED on the Power Board."""
    pb = PowerBoard(MockPowerBoardBackend())

    assert type(pb._error_led) is LED


def test_power_board_wait_start() -> None:
    """Test the wait_for_start_flash method."""
    pb = PowerBoard(MockPowerBoardBackend())

    # Note: This isn't a great test, but ensures that the code runs at least.
    pb.wait_for_start_flash()

    assert pb._run_led.state
