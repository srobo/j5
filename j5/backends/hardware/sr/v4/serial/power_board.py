"""Hardware Backend for the SR V4 power board."""

from datetime import timedelta
import threading
from time import sleep
from typing import Set, cast, Optional, NamedTuple, Dict

from serial import SerialException, SerialTimeoutException
from serial.tools.list_ports_common import ListPortInfo

from j5.backends import Backend
from j5.backends.hardware import DeviceMissingSerialNumberError, NotSupportedByHardwareError
from j5.backends.hardware.j5.serial import SerialHardwareBackend
from j5.boards import Board
from j5.boards.sr.v4.power_board import PowerBoard
from j5.components import (
    BatterySensorInterface,
    ButtonInterface,
    LEDInterface,
    PiezoInterface,
    PowerOutputInterface,
)
from j5.backends import CommunicationError


class BoardIdentity(NamedTuple):

    vendor: str
    board: str
    asset_tag: str
    software_version: str


def is_power_board(port: ListPortInfo) -> bool:
    """
    Check if a ListPortInfo represents a PBV4B.

    We know that the Power Board must be running compatible firmware
    as it must expose a serial interface to be listed.

    :param port: ListPortInfo object.
    :returns: True if object represents a power board.
    """
    return port.manufacturer == "Student Robotics" and port.product == "PBV4B" \
        and port.vid == 0x1bda and port.pid == 0x0010


class SRV4SerialProtocolPowerBoardHardwareBackend(
    SerialHardwareBackend,
    PowerOutputInterface,
    PiezoInterface,
    ButtonInterface,
    BatterySensorInterface,
    LEDInterface,
):
    """The hardware implementation of the SR V4 power board using the serial protocol."""

    board = PowerBoard

    @classmethod
    def discover(cls) -> Set[Board]:
        """
        Discover boards that this backend can control.

        :returns: set of boards that this backend can control.
        :raises DeviceMissingSerialNumberError: a board without a serial number was found.
        """
        # Find all serial ports.
        ports = cls.get_comports()

        # Get a list of boards from the ports.
        boards: Set[Board] = set()
        for port in filter(is_power_board, ports):
            if port.serial_number is None:
                raise DeviceMissingSerialNumberError(
                    "Found power board-like device without serial number. "
                    f"The power board is likely to be damaged: {port.usb_info()}",
                )
            else:
                boards.add(
                    PowerBoard(
                        port.serial_number,
                        cast(
                            Backend,
                            cls(port.device),
                        ),
                    ),
                )

        return boards

    def __init__(
            self,
            serial_port: str,
    ) -> None:
        super().__init__(
            serial_port=serial_port,
            baud=115200,
        )
        self._lock = threading.Lock()
        self._led_states: Dict[int, bool] = {
            i: False
            for i in range(2)
        }
        self.check_firmware_version_supported()
        self.reset_board()

    def check_firmware_version_supported(self) -> None:
        """
        Raises an exception if the firmware version is not supported.

        :raises NotImplementedError: power board is running unsupported firmware
        """
        version = self.firmware_version
        if not version.startswith("4."):
            raise NotImplementedError(f"This power board is running firmware "
                                      f"version {version}, but only version 4.x is supported.")

    def request(self, command: str) -> Optional[str]:
        """
        Sends a request to the power board.

        :returns: Response, if any.
        """
        request_data = command.encode("ascii") + b'\n'  # TODO: Handle emoji lol

        with self._lock:
            try:
                bytes_written = self._serial.write(request_data)
                if len(request_data) != bytes_written:
                    raise CommunicationError(
                        "Mismatch in command bytes written to serial interface.",
                    )
            except SerialTimeoutException as e:
                raise CommunicationError(f"Serial Timeout Error: {e}") from e
            except SerialException as e:
                raise CommunicationError(f"Serial Error: {e}") from e

            response = self.read_serial_line()  # TODO: Handle decoding errors (Is this a bug elsewhere in j5? (yes))

        if response[:4] == "NACK":
            _, error_string = response.split(":", 1)
            raise CommunicationError(f"Power Board returned an error: {error_string}")

        expects_response = command[-1:] == "?"
        if expects_response:
            return response
        elif response == "ACK":
            return None
        else:
            raise CommunicationError(f"Expected ACK from Power Board, but got: {response}")

    def request_with_response(self, command: str) -> str:
        if not command.endswith('?'):
            raise ValueError(f"The provided command does not expect a response: {command}")

        response = self.request(command)
        if response is not None:
            return response
        else:
            raise CommunicationError("Power board responded with ACK but expected data.")

    # TODO: Can we cache this?
    def get_identity(self) -> BoardIdentity:
        """
        Get the board identity information.

        :raises CommunicationError: the identity response did not match the expected format.
        :returns: A tuple of board identity information
        """
        response = self.request("*IDN?")  # TODO: Handle None here?
        parts = response.split(":", 4)
        if len(parts) != 4:
            raise CommunicationError(f"Identify response did not match format: {response}")
        else:
            return BoardIdentity(*parts)

    def reset_board(self) -> None:
        self.request("*RESET")

    @property
    def firmware_version(self) -> str:
        """
        The firmware version reported by the board.

        :returns: firmware version reported by the board, if any.
        """
        identity = self.get_identity()
        return identity.software_version

    def get_power_output_enabled(self, identifier: int) -> bool:
        """
        Get whether a power output is enabled.

        :param identifier: power output to fetch status of.
        :returns: status of the power output.
        :raises ValueError: Invalid power output identifier.
        """
        if identifier in range(6):
            response = self.request_with_response(f"OUT:{identifier}:GET?")
            if response == "0":
                return False
            elif response == "1":
                return True
            else:
                raise CommunicationError(f"Invalid response received: {response}")
        else:
            raise ValueError(f"Invalid identifier: {identifier!r}")

    def set_power_output_enabled(
        self, identifier: int, enabled: bool,
    ) -> None:
        """
        Set whether a power output is enabled.

        :param identifier: power output to enable / disable
        :param enabled: status of the power output.
        :raises ValueError: Invalid power output identifier.
        """
        if identifier in range(6):
            state = "1" if enabled else "0"
            self.request(f"OUT:{identifier}:SET:{state}")
        else:
            raise ValueError(f"Invalid identifier: {identifier!r}")

    def get_power_output_current(self, identifier: int) -> float:
        """
        Get the current being drawn on a power output, in amperes.

        :param identifier: power output to fetch current of.
        :returns: current of the output.
        :raises ValueError: Invalid power output identifier.
        """
        if identifier in range(6):
            response = self.request_with_response(f"OUT:{identifier}:I?")
            return float(response)
        else:
            raise ValueError(f"Invalid identifier: {identifier!r}")

    def buzz(
        self,
        identifier: int,
        duration: timedelta,
        frequency: float,
        blocking: bool,
    ) -> None:
        """
        Queue a pitch to be played.

        :param identifier: piezo identifier to play pitch on.
        :param duration: duration of the tone.
        :param frequency: Pitch of the tone in Hz.
        :param blocking: whether the code waits for the buzz
        :raises ValueError: invalid value for parameter.
        :raises CommunicationError: buzz commands sent too quickly
        :raises NotSupportedByHardwareError: unsupported pitch freq or length.
        """
        if identifier != 0:
            raise ValueError(f"Invalid piezo identifier {identifier!r}; "
                             f"the only valid identifier is 0.")

        duration_ms = round(duration / timedelta(milliseconds=1))
        if duration_ms > 65535:
            raise NotSupportedByHardwareError("Maximum piezo duration is 65535ms.")

        frequency_int = int(round(frequency))
        if frequency_int > 65535:
            raise NotSupportedByHardwareError("Maximum piezo frequency is 65535Hz.")

        self.request(f"NOTE:{frequency_int}:{duration_ms}")

        if blocking:
            sleep(duration.total_seconds())

    def get_button_state(self, identifier: int) -> bool:
        """
        Get the state of a button.

        :param identifier: Button identifier to fetch state of.
        :returns: state of the button.
        :raises ValueError: invalid button identifier.
        """
        if identifier != 0:
            raise ValueError(f"Invalid button identifier {identifier!r}; "
                             f"the only valid identifier is 0.")
        response = self.request_with_response("BTN:START:GET?")
        internal_button, external_button = response.split(":", 1)
        if internal_button == "1" or external_button == "1":
            return True
        elif internal_button == "0" or external_button == "0":
            return False
        else:
            raise CommunicationError(f"Invalid response received: {response}")

    def wait_until_button_pressed(self, identifier: int) -> None:
        """
        Halt the program until this button is pushed.

        :param identifier: Button identifier to wait for.
        """
        while not self.get_button_state(0):
            sleep(0.05)

    def get_battery_sensor_voltage(self, identifier: int) -> float:
        """
        Get the voltage of a battery sensor.

        :param identifier: Identifier of battery sensor.
        :returns: voltage measured by the sensor.
        :raises ValueError: invalid battery sensor identifier.
        """
        if identifier != 0:
            raise ValueError(f"Invalid battery sensor identifier {identifier!r}; "
                             f"the only valid identifier is 0.")
        response = self.request_with_response(f"BATT:V?")
        return float(response)

    def get_battery_sensor_current(self, identifier: int) -> float:
        """
        Get the current of a battery sensor.

        :param identifier: Identifier of battery sensor.
        :returns: current measured by the sensor.
        :raises ValueError: invalid battery sensor identifier.
        """
        if identifier != 0:
            raise ValueError(f"Invalid battery sensor identifier {identifier!r}; "
                             f"the only valid identifier is 0.")
        response = self.request_with_response(f"BATT:I?")
        return float(response)

    def get_led_state(self, identifier: int) -> bool:
        """
        Get the state of an LED.

        :param identifier: identifier of the LED.
        :returns: current state of the LED.
        """
        return self._led_states[identifier]

    def set_led_state(self, identifier: int, state: bool) -> None:
        """
        Set the state of an LED.

        :param identifier: identifier of the LED.
        :param state: desired state of the LED.
        :raises ValueError: invalid LED identifer.
        """
        if identifier > 1:
            raise ValueError(f"Invalid LED identifier {identifier!r}; "
                             f"the only valid identifiers are 0 and 1.")
        led_names = ["RUN", "ERR"]

        self.request(f"LED:{led_names[identifier]}:SET:{int(state)}")
