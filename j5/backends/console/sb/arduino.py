"""Console Backend for the SourceBots Arduino."""
from datetime import timedelta
from typing import List, Optional, Set, Type, cast

from j5.backends.console import Console
from j5.backends.console.j5.arduino import ArduinoConsoleBackend
from j5.boards import Board
from j5.boards.sb import SBArduinoBoard
from j5.components import GPIOPinMode, ServoInterface, ServoPosition
from j5.components.derived import UltrasoundInterface


class SBArduinoConsoleBackend(
    ServoInterface,
    UltrasoundInterface,
    ArduinoConsoleBackend,
):
    """Console Backend for the SourceBots Arduino."""

    board = SBArduinoBoard

    def __init__(self, serial: str, console_class: Type[Console] = Console) -> None:
        super().__init__(serial, console_class)

        self._servo_states: List[ServoPosition] = [None] * 16

    @classmethod
    def discover(cls) -> Set[Board]:
        """
        Discover boards that this backend can control.

        :returns: set of boards that this backend can control.
        """
        return {cast(Board, SBArduinoBoard("SERIAL", cls("SERIAL")))}

    def get_servo_position(self, identifier: int) -> ServoPosition:
        """
        Get the position of a servo.

        :param identifier: Port of servo to check.
        :returns: Position of servo.
        """
        return self._servo_states[identifier]

    def set_servo_position(
            self,
            identifier: int,
            position: ServoPosition,
    ) -> None:
        """
        Set the position of a servo.

        :param identifier: Port of servo to set position.
        :param position: Position to set the servo to.
        """
        self._servo_states[identifier] = position
        self._console.info(f"Set servo {identifier} to {position}")

    def get_ultrasound_pulse(
            self,
            trigger_pin_identifier: int,
            echo_pin_identifier: int,
    ) -> Optional[timedelta]:
        """
        Get a timedelta for the ultrasound time.

        :param trigger_pin_identifier: pin number of the trigger pin.
        :param echo_pin_identifier: pin number of the echo pin.
        :returns: Time taken for the pulse, or None if it timed out.
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
        """
        Get a distance in metres.

        :param trigger_pin_identifier: pin number of the trigger pin.
        :param echo_pin_identifier: pin number of the echo pin.
        :returns: Distance measured in metres, or None if it timed out.
        """
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
        """
        Ultrasound functions force the pins into particular modes.

        :param trigger_pin_identifier: pin number of the trigger pin.
        :param echo_pin_identifier: pin number of the echo pin.
        """
        self._pins[trigger_pin_identifier].mode = GPIOPinMode.DIGITAL_OUTPUT
        self._pins[trigger_pin_identifier].digital_state = False
        self._pins[echo_pin_identifier].mode = GPIOPinMode.DIGITAL_INPUT
