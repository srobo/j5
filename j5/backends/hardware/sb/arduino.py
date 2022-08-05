"""SourceBots Arduino Hardware Implementation."""

from datetime import timedelta
from typing import List, Optional

from serial import SerialException, SerialTimeoutException

from j5.backends import CommunicationError
from j5.backends.hardware.env import NotSupportedByHardwareError
from j5.backends.hardware.j5.arduino import ArduinoHardwareBackend
from j5.boards.sb.arduino import SBArduinoBoard
from j5.components import GPIOPinMode, ServoInterface, ServoPosition
from j5.components.derived import UltrasoundInterface


class SBArduinoHardwareBackend(
    ServoInterface,
    UltrasoundInterface,
    ArduinoHardwareBackend,
):
    """Hardware Backend for the SourceBots Arduino Uno."""

    board = SBArduinoBoard

    def __init__(
            self,
            serial_port: str,
    ):
        super().__init__(serial_port)

        # Initialise stored servo states
        self._servo_states: List[ServoPosition] = [None] * 16

        # Verify that the Arduino has booted
        count = 0
        line = self.read_serial_line(empty=True)
        while len(line) == 0:
            line = self.read_serial_line(empty=True)
            count += 1
            if count > 25:
                raise CommunicationError(
                    f"Arduino ({self.serial_port}) is not responding",
                )
        if line != "# Booted":
            raise CommunicationError("Arduino Boot Error.")
        self._version_line = self.read_serial_line()

        # Verify that the Arduino firmware meets or exceeds the minimum version
        version_ids = tuple(map(int, self.firmware_version.split(".")))
        if version_ids < (2019, 6, 0) or len(version_ids) != 3:
            raise CommunicationError(
                f"Unexpected firmware version: {self.firmware_version},"
                f" expected at least: \"2019.6.0\".",
            )

    @property
    def firmware_version(self) -> str:
        """
        The firmware version reported by the board.

        :returns: firmware version reported by the board.
        """
        return self._version_line.split("v")[1]

    def _command(self, command: str, *params: str) -> List[str]:
        """
        Send a command to the board.

        :param command: Command to send to the board:
        :param params: Additional parameters to the command.
        :returns: List of responses from the board.
        :raises CommunicationError: An error occurred during the command execution.
        """
        try:
            with self._lock:
                message = " ".join([command] + list(params)) + "\n"
                self._serial.write(message.encode("utf-8"))

                results: List[str] = []
                while True:
                    line = self.read_serial_line(empty=False)
                    code, param = line.split(None, 1)
                    if code == "+":
                        return results
                    elif code == "-":
                        raise CommunicationError(f"Arduino error: {param}")
                    elif code == ">":
                        results.append(param)
                    elif code == "#":
                        pass  # Ignore comment lines
                    else:
                        raise CommunicationError(
                            f"Arduino returned unrecognised response line: {line}",
                        )
        except SerialTimeoutException as e:
            raise CommunicationError(f"Serial Timeout Error: {e}") from e
        except SerialException as e:
            raise CommunicationError(f"Serial Error: {e}") from e

    def _update_digital_pin(self, identifier: int) -> None:
        """
        Write the stored value of a digital pin to the Arduino.

        Reads the state out of self._digital_pins.

        :param identifier: Pin number to update.
        :raises RuntimeError: Pin is an analogue pin.
        """
        if identifier >= SBArduinoBoard.FIRST_ANALOGUE_PIN:
            raise RuntimeError("Reached an unreachable statement.")
        pin = self._digital_pins[identifier]
        char: str
        if pin.mode == GPIOPinMode.DIGITAL_INPUT:
            char = "Z"
        elif pin.mode == GPIOPinMode.DIGITAL_INPUT_PULLUP:
            char = "P"
        elif pin.mode == GPIOPinMode.DIGITAL_OUTPUT:
            if pin.state:
                char = "H"
            else:
                char = "L"
        else:
            raise RuntimeError("Reached an unreachable statement.")
        self._command("W", str(identifier), char)

    def _read_digital_pin(self, identifier: int) -> bool:
        """
        Read the value of a digital pin from the Arduino.

        :param identifier: pin number to read value of.
        :returns: state of the pin.
        :raises CommunicationError: something went wrong during arduino comms.
        """
        results = self._command("R", str(identifier))
        if len(results) != 1:
            raise CommunicationError(f"Invalid response from Arduino: {results!r}")
        result = results[0]
        if result == "H":
            return True
        elif result == "L":
            return False
        else:
            raise CommunicationError(f"Invalid response from Arduino: {result!r}")

    def _read_analogue_pin(self, identifier: int) -> float:
        """
        Read the value of an analogue pin from the Arduino.

        :param identifier: pin number to read value of.
        :returns: analogue value of the pin.
        :raises NotSupportedByHardwareError: pin does not have ADC functionality.
        :raises CommunicationError: something went wrong during arduino comms.
        """
        if identifier >= SBArduinoBoard.FIRST_ANALOGUE_PIN + 4:
            raise NotSupportedByHardwareError(
                "Arduino Uno firmware only supports analogue pins 0-3 (IDs 14-17)",
            )
        analogue_pin_num = identifier - 14
        results = self._command("A")
        for result in results:
            pin_name, reading = result.split(None, 1)
            if pin_name == f"a{analogue_pin_num}":
                voltage = (int(reading) / 1024.0) * 5.0
                return voltage
        raise CommunicationError(f"Invalid response from Arduino: {results!r}")

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
        :raises ValueError: Position was not valid.
        """
        if position is None:
            level = 0
        elif -1 <= position <= 1:
            # Adjust to be in the range 0-1
            status_unit = (position + 1) / 2
            level = 150 + int((550 - 150) * status_unit)
        else:
            raise ValueError("Position of servo should be between 1 and -1.")

        self._command('S', str(identifier), str(level))
        self._servo_states[identifier] = position

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
        :raises CommunicationError: Invalid response from Arduino
        """
        self._check_ultrasound_pins(trigger_pin_identifier, echo_pin_identifier)
        results = self._command("T", str(trigger_pin_identifier),
                                str(echo_pin_identifier))
        self._update_ultrasound_pin_modes(trigger_pin_identifier, echo_pin_identifier)
        if len(results) != 1:
            raise CommunicationError(f"Invalid response from Arduino: {results!r}")
        result = results[0]
        microseconds = float(result)
        if microseconds == 0:
            # arduino pulseIn() returned 0 which indicates a timeout.
            return None
        else:
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
        :raises CommunicationError: Invalid response from Arduino
        """
        self._check_ultrasound_pins(trigger_pin_identifier, echo_pin_identifier)
        results = self._command("U", str(trigger_pin_identifier),
                                str(echo_pin_identifier))
        self._update_ultrasound_pin_modes(trigger_pin_identifier, echo_pin_identifier)
        if len(results) != 1:
            raise CommunicationError(f"Invalid response from Arduino: {results!r}")
        result = results[0]
        millimetres = float(result)
        if millimetres == 0:
            # arduino pulseIn() returned 0 which indicates a timeout.
            return None
        else:
            return millimetres / 1000.0

    @staticmethod
    def _check_ultrasound_pins(
            trigger_pin_identifier: int,
            echo_pin_identifier: int,
    ) -> None:
        """
        Verify the validity of a pair of ultrasound pins.

        :param trigger_pin_identifier: pin number of the trigger pin.
        :param echo_pin_identifier: pin number of the echo pin.
        :raises NotSupportedByHardwareError: Ultrasound not supported on analogue pins
        """
        if trigger_pin_identifier >= SBArduinoBoard.FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Ultrasound functions not supported on analogue pins",
            )
        if echo_pin_identifier >= SBArduinoBoard.FIRST_ANALOGUE_PIN:
            raise NotSupportedByHardwareError(
                "Ultrasound functions not supported on analogue pins",
            )

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
        self._digital_pins[trigger_pin_identifier].mode = GPIOPinMode.DIGITAL_OUTPUT
        self._digital_pins[trigger_pin_identifier].state = False
        self._digital_pins[echo_pin_identifier].mode = GPIOPinMode.DIGITAL_INPUT
