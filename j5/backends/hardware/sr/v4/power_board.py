"""Hardware Backend for the SR V4 power board."""

import struct
from datetime import timedelta
from time import sleep
from typing import Callable, Dict, Mapping, Set, cast

import usb

from j5.backends.hardware.env import (
    HardwareEnvironment,
    NotSupportedByHardwareError,
)
from j5.backends.hardware.j5.raw_usb import (
    RawUSBHardwareBackend,
    ReadCommand,
    WriteCommand,
    handle_usb_error,
)
from j5.boards import Board
from j5.boards.sr.v4.power_board import PowerBoard, PowerOutputPosition
from j5.components import (
    BatterySensorInterface,
    ButtonInterface,
    LEDInterface,
    PiezoInterface,
    PowerOutputInterface,
)

# The names and codes of these commands match the definitions in usb.h in the firmware
# source.
CMD_READ_OUTPUT: Mapping[int, ReadCommand] = {
    output.value: ReadCommand(output.value, 4)
    for output in PowerOutputPosition
}
CMD_READ_5VRAIL = ReadCommand(6, 4)
CMD_READ_BATTERY = ReadCommand(7, 8)
CMD_READ_BUTTON = ReadCommand(8, 4)
CMD_READ_FWVER = ReadCommand(9, 4)

CMD_WRITE_OUTPUT: Mapping[int, WriteCommand] = {
    output.value: WriteCommand(output.value)
    for output in PowerOutputPosition
}
CMD_WRITE_RUNLED = WriteCommand(6)
CMD_WRITE_ERRORLED = WriteCommand(7)
CMD_WRITE_PIEZO = WriteCommand(8)


class SRV4PowerBoardHardwareBackend(
    PowerOutputInterface,
    PiezoInterface,
    ButtonInterface,
    BatterySensorInterface,
    LEDInterface,
    RawUSBHardwareBackend,
):
    """The hardware implementation of the SR V4 power board."""

    environment = HardwareEnvironment
    board = PowerBoard

    @classmethod
    @handle_usb_error
    def discover(cls, find: Callable = usb.core.find) -> Set[Board]:
        """Discover boards that this backend can control."""
        boards: Set[Board] = set()
        device_list = find(idVendor=0x1bda, idProduct=0x0010, find_all=True)
        for device in device_list:
            backend = cls(device)
            board = PowerBoard(backend)
            boards.add(cast(Board, board))
        return boards

    @handle_usb_error
    def __init__(self, usb_device: usb.core.Device) -> None:
        self._usb_device = usb_device

        self._output_states: Dict[int, bool] = {
            output.value: False
            for output in PowerOutputPosition
        }
        self._led_states: Dict[int, bool] = {
            i: False
            for i in range(2)
        }
        self.check_firmware_version_supported()

    def check_firmware_version_supported(self) -> None:
        """Raises an exception if the firmware version is not supported."""
        v = self.firmware_version
        if v != "3":
            raise NotImplementedError(f"this power board is running firmware "
                                      f"version {v}, but only version 3 is supported")

    @property
    def firmware_version(self) -> str:
        """The firmware version reported by the board."""
        version, = struct.unpack("<I", self._read(CMD_READ_FWVER))
        return str(cast(int, version))

    def get_power_output_enabled(self, identifier: int) -> bool:
        """Get whether a power output is enabled."""
        try:
            return self._output_states[identifier]
        except KeyError:
            raise ValueError(f"Invalid power output identifier {identifier!r}; "
                             f"valid identifiers are {CMD_WRITE_OUTPUT.keys()}") from None

    def set_power_output_enabled(
        self, identifier: int, enabled: bool,
    ) -> None:
        """Set whether a power output is enabled."""
        try:
            cmd = CMD_WRITE_OUTPUT[identifier]
        except KeyError:
            raise ValueError(f"Invalid power output identifier {identifier!r}; "
                             f"valid identifiers are {CMD_WRITE_OUTPUT.keys()}") from None
        self._write(cmd, int(enabled))
        self._output_states[identifier] = enabled

    def get_power_output_current(self, identifier: int) -> float:
        """Get the current being drawn on a power output, in amperes."""
        try:
            cmd = CMD_READ_OUTPUT[identifier]
        except KeyError:
            raise ValueError(f"invalid power output identifier {identifier!r}; "
                             f"valid identifiers are {CMD_READ_OUTPUT.keys()}") from None
        current, = struct.unpack("<I", self._read(cmd))
        return cast(int, current) / 1000  # convert milliamps to amps

    def buzz(self, identifier: int,
             duration: timedelta, frequency: float) -> None:
        """Queue a pitch to be played."""
        if identifier != 0:
            raise ValueError(f"invalid piezo identifier {identifier!r}; "
                             f"the only valid identifier is 0")

        duration_ms = round(duration / timedelta(milliseconds=1))
        if duration_ms > 65535:
            raise NotSupportedByHardwareError("Maximum piezo duration is 65535ms.")

        frequency_int = int(round(frequency))
        if frequency_int > 65535:
            raise NotSupportedByHardwareError("Maximum piezo frequency is 65535Hz.")

        data = struct.pack("<HH", frequency_int, duration_ms)
        self._write(CMD_WRITE_PIEZO, data)

    def get_button_state(self, identifier: int) -> bool:
        """Get the state of a button."""
        if identifier != 0:
            raise ValueError(f"invalid button identifier {identifier!r}; "
                             f"the only valid identifier is 0")
        state, = struct.unpack("<I", self._read(CMD_READ_BUTTON))
        return cast(int, state) != 0

    def wait_until_button_pressed(self, identifier: int) -> None:
        """Halt the program until this button is pushed."""
        while not self.get_button_state(identifier):
            sleep(0.05)

    def get_battery_sensor_voltage(self, identifier: int) -> float:
        """Get the voltage of a battery sensor."""
        if identifier != 0:
            raise ValueError(f"invalid battery sensor identifier {identifier!r}; "
                             f"the only valid identifier is 0")
        current, voltage = struct.unpack("<II", self._read(CMD_READ_BATTERY))
        return cast(int, voltage) / 1000  # convert millivolts to volts

    def get_battery_sensor_current(self, identifier: int) -> float:
        """Get the current of a battery sensor."""
        if identifier != 0:
            raise ValueError(f"invalid battery sensor identifier {identifier!r}; "
                             f"the only valid identifier is 0")
        current, voltage = struct.unpack("<II", self._read(CMD_READ_BATTERY))
        return cast(int, current) / 1000  # convert milliamps to amps

    def get_led_state(self, identifier: int) -> bool:
        """Get the state of an LED."""
        return self._led_states[identifier]

    def set_led_state(self, identifier: int, state: bool) -> None:
        """Set the state of an LED."""
        cmds = {0: CMD_WRITE_RUNLED, 1: CMD_WRITE_ERRORLED}
        try:
            cmd = cmds[identifier]
        except KeyError:
            raise ValueError(f"invalid LED identifier {identifier!r}; valid identifiers "
                             f"are 0 (run LED) and 1 (error LED)") from None
        self._write(cmd, int(state))
        self._led_states[identifier] = state
