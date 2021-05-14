"""Console Backend for the SourceBots Arduino."""
from datetime import timedelta
from typing import Optional, Set, cast

from j5.backends.console.j5.arduino import ArduinoConsoleBackend
from j5.boards import Board
from j5.boards.sb import SBArduinoBoard
from j5.components import GPIOPinMode
from j5.components.derived import UltrasoundInterface


class SBArduinoConsoleBackend(
    UltrasoundInterface,
    ArduinoConsoleBackend,
):
    """Console Backend for the SourceBots Arduino."""

    board = SBArduinoBoard

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover boards that this backend can control."""
        return {cast(Board, SBArduinoBoard("SERIAL", cls("SERIAL")))}

    def get_ultrasound_pulse(
            self,
            trigger_pin_identifier: int,
            echo_pin_identifier: int,
    ) -> Optional[timedelta]:
        """
        Get a timedelta for the ultrasound time.

        Returns None if the sensor times out.
        """
        microseconds = self._console.read(
            f"Response time for ultrasound sensor on pins "
            f"{trigger_pin_identifier}/{echo_pin_identifier} [microseconds]",
            float,
        )
        self._update_ultrasound_pin_modes(trigger_pin_identifier, echo_pin_identifier)
        return timedelta(microseconds=microseconds)

    def get_ultrasound_distance(
            self,
            trigger_pin_identifier: int,
            echo_pin_identifier: int,
    ) -> Optional[float]:
        """Get a distance in metres."""
        metres = self._console.read(
            f"Distance for ultrasound sensor on pins "
            f"{trigger_pin_identifier}/{echo_pin_identifier} [metres]",
            float,
        )
        self._update_ultrasound_pin_modes(trigger_pin_identifier, echo_pin_identifier)
        return metres

    def _update_ultrasound_pin_modes(
        self,
        trigger_pin_identifier: int,
        echo_pin_identifier: int,
    ) -> None:
        # Ultrasound functions force the pins into particular modes.
        self._pins[trigger_pin_identifier].mode = GPIOPinMode.DIGITAL_OUTPUT
        self._pins[trigger_pin_identifier].digital_state = False
        self._pins[echo_pin_identifier].mode = GPIOPinMode.DIGITAL_INPUT
