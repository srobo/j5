"""Console Backend for the SR V4 power board."""

from datetime import timedelta
from typing import Dict, Optional, Set, Type, cast

from j5.backends import Backend
from j5.backends.console.console import Console
from j5.boards import Board
from j5.boards.sr.v4.power_board import PowerBoard, PowerOutputPosition
from j5.components import (
    BatterySensorInterface,
    ButtonInterface,
    LEDInterface,
    PiezoInterface,
    PowerOutputInterface,
)


class SRV4PowerBoardConsoleBackend(
    PowerOutputInterface,
    PiezoInterface,
    ButtonInterface,
    BatterySensorInterface,
    LEDInterface,
    Backend,
):
    """The console implementation of the SR V4 power board."""

    board = PowerBoard

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover boards that this backend can control."""
        return {cast(Board, PowerBoard("SERIAL", cls("SERIAL")))}

    def __init__(self, serial: str, console_class: Type[Console] = Console) -> None:
        self._serial = serial
        self._output_states: Dict[int, bool] = {
            output.value: False
            for output in PowerOutputPosition
        }
        self._led_states: Dict[int, bool] = {
            i: False
            for i in range(2)
        }

        # Setup console helper
        self._console = console_class(f"{self.board.__name__}({self._serial})")

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version reported by the board."""
        return None  # Console, so no firmware

    @property
    def serial(self) -> str:
        """The serial number reported by the board."""
        return self._serial

    def get_power_output_enabled(self, identifier: int) -> bool:
        """Get whether a power output is enabled."""
        try:
            return self._output_states[identifier]
        except KeyError:
            raise ValueError(f"Invalid power output identifier {identifier!r}; "
                             f"valid identifiers are "
                             f"{self._output_states.keys()}") from None

    def set_power_output_enabled(
        self, identifier: int, enabled: bool,
    ) -> None:
        """Set whether a power output is enabled."""
        self._console.info(f"Setting output {identifier} to {enabled}")
        if identifier not in self._output_states.keys():
            raise ValueError(f"Invalid power output identifier {identifier!r}; "
                             f"valid identifiers are "
                             f"{self._output_states.keys()}")
        self._output_states[identifier] = enabled

    def get_power_output_current(self, identifier: int) -> float:
        """Get the current being drawn on a power output, in amperes."""
        if identifier in self._output_states:

            return self._console.read(
                f"Current for power output {identifier} [amps]",
                float,
            )
        else:
            raise ValueError(f"Invalid power output identifier {identifier!r}; "
                             f"valid identifiers are "
                             f"{self._output_states.keys()}") from None

    def buzz(self, identifier: int,
             duration: timedelta, pitch: float) -> None:
        """Queue a pitch to be played."""
        if identifier != 0:
            raise ValueError(f"invalid piezo identifier {identifier!r}; "
                             f"the only valid identifier is 0")
        duration_ms = round(duration / timedelta(milliseconds=1))
        if duration_ms > 65535:
            raise ValueError("Maximum piezo duration is 65535ms.")
        self._console.info(f"Buzzing at {pitch}Hz for {duration_ms}ms")

    def get_button_state(self, identifier: int) -> bool:
        """Get the state of a button."""
        if identifier != 0:
            raise ValueError(f"invalid button identifier {identifier!r}; "
                             f"the only valid identifier is 0")
        return self._console.read("Start button state [true/false]", bool)

    def wait_until_button_pressed(self, identifier: int) -> None:
        """Halt the program until this button is pushed."""
        self._console.info("Waiting for start button press.")
        self._console.read("Hit return to press start button", None)

    def get_battery_sensor_voltage(self, identifier: int) -> float:
        """Get the voltage of a battery sensor."""
        if identifier != 0:
            raise ValueError(f"invalid battery sensor identifier {identifier!r}; "
                             f"the only valid identifier is 0")
        return self._console.read("Battery voltage [volts]", float)

    def get_battery_sensor_current(self, identifier: int) -> float:
        """Get the current of a battery sensor."""
        if identifier != 0:
            raise ValueError(f"invalid battery sensor identifier {identifier!r}; "
                             f"the only valid identifier is 0")
        return self._console.read("Battery current [amps]", float)

    def get_led_state(self, identifier: int) -> bool:
        """Get the state of an LED."""
        return self._led_states[identifier]

    def set_led_state(self, identifier: int, state: bool) -> None:
        """Set the state of an LED."""
        if identifier in self._led_states.keys():
            self._console.info(f"Set LED {identifier} to {state}")
            self._led_states[identifier] = state
        else:
            raise ValueError(f"invalid LED identifier {identifier!r}; valid identifiers "
                             f"are 0 (run LED) and 1 (error LED)") from None
