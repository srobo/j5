"""Hardware Backend for the SR V4 power board."""
import threading
from datetime import timedelta
from time import sleep
from typing import Dict, Set, cast

from serial.tools.list_ports_common import ListPortInfo

from j5.backends import Backend, CommunicationError
from j5.backends.hardware import (
    DeviceMissingSerialNumberError,
    NotSupportedByHardwareError,
)
from j5.backends.hardware.sr.v4.serial.protocol import (
    SRV4SerialProtocolBackend,
)
from j5.boards import Board
from j5.boards.sr.v4.power_board import PowerBoard
from j5.components import (
    BatterySensorInterface,
    ButtonInterface,
    LEDInterface,
    PiezoInterface,
    PowerOutputInterface,
)

LED_NAMES = ("RUN", "ERR")
MAX_BUZZ_DURATION_MS = (2 ** 31) - 1  # int32 max
SUPPORTED_MAJOR_VERSIONS = {4}


def is_power_board(port: ListPortInfo) -> bool:
    """
    Check if a ListPortInfo represents a PBV4B.

    We know that the Power Board must be running compatible firmware
    as it must expose a serial interface to be listed.

    :param port: ListPortInfo object.
    :returns: True if object represents a power board.
    """
    return port.manufacturer == "Student Robotics" and port.product == "Power Board v4" \
        and port.vid == 0x1bda and port.pid == 0x0010


class SRV4SerialProtocolPowerBoardHardwareBackend(
    SRV4SerialProtocolBackend,
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
            0: False,
            1: False,
        }
        self._check_firmware_version_supported(
            self.firmware_version, SUPPORTED_MAJOR_VERSIONS,
        )
        self.reset_board()

    def get_features(self) -> Set['Board.AvailableFeatures']:
        """
        The set of features available on this backend.

        :returns: The set of features available on this backend.
        """
        return {
            PowerBoard.AvailableFeatures.REG_5V_CONTROL,
            PowerBoard.AvailableFeatures.BRAIN_OUTPUT,
        }

    def get_power_output_enabled(self, identifier: int) -> bool:
        """
        Get whether a power output is enabled.

        :param identifier: power output to fetch status of.
        :returns: status of the power output.
        :raises CommunicationError: Invalid response received.
        :raises ValueError: Invalid power output identifier.
        """
        if identifier in range(7):
            response = self.query(f"OUT:{identifier}:GET?")
            if response == "0":
                return False
            elif response == "1":
                return True
            else:
                raise CommunicationError(
                    f"Power Board returned an invalid response: {response}")
        else:
            raise ValueError(f"{identifier!r} is not a valid power output identifier")

    def set_power_output_enabled(
        self, identifier: int, enabled: bool,
    ) -> None:
        """
        Set whether a power output is enabled.

        :param identifier: power output to enable / disable
        :param enabled: status of the power output.
        :raises ValueError: Invalid power output identifier.
        """
        if identifier in range(7):
            state = "1" if enabled else "0"
            self.request(f"OUT:{identifier}:SET:{state}")
        else:
            raise ValueError(f"{identifier!r} is not a valid power output identifier")

    def get_power_output_current(self, identifier: int) -> float:
        """
        Get the current being drawn on a power output, in amperes.

        :param identifier: power output to fetch current of.
        :returns: current of the output.
        :raises ValueError: Invalid power output identifier.
        """
        if identifier in range(7):
            response = self.query(f"OUT:{identifier}:I?")
            return self._parse_float(response) / 1000
        else:
            raise ValueError(f"{identifier!r} is not a valid power output identifier")

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
        :raises NotSupportedByHardwareError: unsupported pitch freq or length.
        """
        if identifier != 0:
            raise ValueError(f"Invalid piezo identifier {identifier!r}; "
                             f"the only valid identifier is 0.")

        duration_ms = round(duration.total_seconds() * 1000)

        if not 0 < duration_ms < MAX_BUZZ_DURATION_MS:
            raise NotSupportedByHardwareError(
                f"Piezo duration must be in range of 0 - {MAX_BUZZ_DURATION_MS}ms.",
            )

        frequency_int = int(round(frequency))
        if not 0 < frequency_int < 10_000:
            raise NotSupportedByHardwareError(
                "Piezo frequency must be in range of 0 - 10kHz.",
            )

        self.request(f"NOTE:{frequency_int}:{duration_ms}")

        if blocking:
            sleep(duration.total_seconds())

    def get_button_state(self, identifier: int) -> bool:
        """
        Get the state of a button.

        :param identifier: Button identifier to fetch state of.
        :returns: state of the button.
        :raises CommunicationError: Invalid response received.
        :raises ValueError: invalid button identifier.
        """
        if identifier != 0:
            raise ValueError(f"Invalid button identifier {identifier!r}; "
                             f"the only valid identifier is 0.")
        response = self.query("BTN:START:GET?")
        if ":" not in response:
            raise CommunicationError(
                f"Power Board returned an invalid response: {response}",
            )

        internal_button, external_button = response.split(":", 1)
        if internal_button == "1" or external_button == "1":
            return True
        elif internal_button == "0" or external_button == "0":
            return False
        else:
            raise CommunicationError(
                f"Power Board returned an invalid response: {response}",
            )

    def wait_until_button_pressed(self, identifier: int) -> None:
        """
        Halt the program until this button is pushed.

        :param identifier: Button identifier to wait for.
        """
        # The start button's state is latched.
        # Meaning that we need to fetch it once beforehand to discard the last response.
        _ = self.get_button_state(identifier)
        while not self.get_button_state(identifier):
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
        response = self.query("BATT:V?")
        return self._parse_float(response) / 1000

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
        response = self.query("BATT:I?")
        return self._parse_float(response) / 1000

    def get_led_state(self, identifier: int) -> bool:
        """
        Get the state of an LED.

        :param identifier: identifier of the LED.
        :raises ValueError: invalid LED identifier.
        :returns: current state of the LED.
        """
        if identifier not in (0, 1):
            raise ValueError(
                f"Invalid LED identifier {identifier!r}; the only valid identifiers"
                " are 0 and 1.",
            )
        return self._led_states[identifier]

    def set_led_state(self, identifier: int, state: bool) -> None:
        """
        Set the state of an LED.

        :param identifier: identifier of the LED.
        :param state: desired state of the LED.
        :raises ValueError: invalid LED identifier.
        """
        if identifier not in (0, 1):
            raise ValueError(
                f"Invalid LED identifier {identifier!r}; the only valid identifiers"
                " are 0 and 1.",
            )
        led_name = LED_NAMES[identifier]
        state_int = int(state)

        self.request(f"LED:{led_name}:SET:{state_int}")
        self._led_states[identifier] = state
