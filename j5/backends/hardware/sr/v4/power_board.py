"""Hardware Backend for the SR V4 power board."""

import struct
from datetime import timedelta
from time import sleep
from typing import Dict, List, NamedTuple, Optional, Union, cast

import usb1

from j5.backends import Backend
from j5.backends.hardware.env import HardwareEnvironment
from j5.boards import Board
from j5.boards.sr.v4.power_board import PowerBoard, PowerOutputPosition
from j5.components import (
    BatterySensorInterface,
    ButtonInterface,
    LEDInterface,
    PiezoInterface,
    PowerOutputInterface,
)
from j5.components.piezo import Note, Pitch


class ReadCommand(NamedTuple):
    """
    Models a command to read information from the power board using USB controlRead.

    code identifies the command in accordance with the definitions in usb.h in the
    firmware source.

    data_len is the number of bytes that will be returned by the command.
    """

    code: int
    data_len: int


class WriteCommand(NamedTuple):
    """
    Models a command to write information to the power board using USB controlWrite.

    code identifies the command in accordance with the definitions in usb.h in the
    firmware source.
    """

    code: int


# The names and codes of these commands match the definitions in usb.h in the firmware
# source.
CMD_READ_OUTPUT = {
    output.value: ReadCommand(output.value, 4)
    for output in PowerOutputPosition
}
CMD_READ_5VRAIL = ReadCommand(6, 4)
CMD_READ_BATTERY = ReadCommand(7, 8)
CMD_READ_BUTTON = ReadCommand(8, 4)
CMD_READ_FWVER = ReadCommand(9, 4)
CMD_WRITE_OUTPUT = {
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
    Backend,
):
    """The hardware implementation of the SR V4 power board."""

    environment = HardwareEnvironment
    board = PowerBoard

    @classmethod
    def discover(cls) -> List[Board]:
        """Discover boards that this backend can control."""
        boards: List[Board] = []
        context = usb1.USBContext()
        for device in context.getDeviceList(skip_on_error=True):
            if device.getVendorID() == 0x1BDA and device.getProductID() == 0x0010:
                backend = cls(device)
                board = PowerBoard(backend.serial, backend)
                boards.append(cast(Board, board))
        return boards

    def __init__(self, usb_device: usb1.USBDevice):
        self._usb_device: usb1.USBDevice = usb_device
        self._usb_handle: usb1.USBDeviceHandle = self._usb_device.open()
        self._output_states: Dict[int, bool] = {
            output.value: False
            for output in PowerOutputPosition
        }
        self._led_states: Dict[int, bool] = {
            i: False
            for i in range(2)
        }
        self.check_firmware_version_supported()

    def _read(self, command: ReadCommand) -> bytes:
        return self._usb_handle.controlRead(0x80, 64, 0, command.code, command.data_len)

    def _write(self, command: WriteCommand, param: Union[int, bytes]) -> None:
        req_val: int = 0
        req_data: bytes = b""
        if isinstance(param, int):
            req_val = param
        else:
            req_data = param
        self._usb_handle.controlWrite(0x00, 64, req_val, command.code, req_data)

    def check_firmware_version_supported(self) -> None:
        """Raises an exception if the firmware version is not supported."""
        v = self.firmware_version
        if v != 3:
            raise NotImplementedError(f"this power board is running firmware "
                                      f"version {v}, but only version 3 is supported")

    @property
    def firmware_version(self) -> int:
        """The firmware version reported by the board."""
        version, = struct.unpack("<I", self._read(CMD_READ_FWVER))
        return cast(int, version)

    @property
    def serial(self) -> str:
        """The serial number reported by the board."""
        return self._usb_device.getSerialNumber()

    def get_firmware_version(self, board: 'Board') -> Optional[str]:
        """Get the firmware version reported by the board."""
        return str(self.firmware_version)

    def get_power_output_enabled(self, board: Board, identifier: int) -> bool:
        """Get whether a power output is enabled."""
        return self._output_states[identifier]

    def set_power_output_enabled(
        self, board: Board, identifier: int, enabled: bool,
    ) -> None:
        """Set whether a power output is enabled."""
        try:
            cmd = CMD_WRITE_OUTPUT[identifier]
        except KeyError:
            raise ValueError(f"invalid power output identifier {identifier!r}; "
                             f"valid identifiers are {CMD_WRITE_OUTPUT.keys()}") from None
        self._write(cmd, int(enabled))
        self._output_states[identifier] = enabled

    def get_power_output_current(self, board: Board, identifier: int) -> float:
        """Get the current being drawn on a power output, in amperes."""
        try:
            cmd = CMD_READ_OUTPUT[identifier]
        except KeyError:
            raise ValueError(f"invalid power output identifier {identifier!r}; "
                             f"valid identifiers are {CMD_READ_OUTPUT.keys()}") from None
        current, = struct.unpack("<I", self._read(cmd))
        return cast(int, current) / 1000  # convert milliamps to amps

    def buzz(self, board: Board, identifier: int,
             duration: timedelta, pitch: Pitch) -> None:
        """Queue a pitch to be played."""
        if identifier != 0:
            raise ValueError(f"invalid piezo identifier {identifier!r}; "
                             f"the only valid identifier is 0")
        if isinstance(pitch, Note):
            frequency = pitch.value
        else:
            frequency = pitch
        duration_ms = round(duration / timedelta(milliseconds=1))
        data = struct.pack("<HH", frequency, duration_ms)
        self._write(CMD_WRITE_PIEZO, data)

    def get_button_state(self, board: Board, identifier: int) -> bool:
        """Get the state of a button."""
        if identifier != 0:
            raise ValueError(f"invalid button identifier {identifier!r}; "
                             f"the only valid identifier is 0")
        state, = struct.unpack("<I", self._read(CMD_READ_BUTTON))
        return cast(int, state) != 0

    def wait_until_button_pressed(self, board: Board, identifier: int) -> bool:
        """Halt the program until this button is pushed."""
        while not self.get_button_state(board, identifier):
            sleep(0.05)
        return self.get_button_state(board, identifier)

    def get_battery_sensor_voltage(self, board: Board, identifier: int) -> float:
        """Get the voltage of a battery sensor."""
        if identifier != 0:
            raise ValueError(f"invalid battery sensor identifier {identifier!r}; "
                             f"the only valid identifier is 0")
        current, voltage = struct.unpack("<II", self._read(CMD_READ_BATTERY))
        return cast(int, voltage) / 1000  # convert millivolts to volts

    def get_battery_sensor_current(self, board: Board, identifier: int) -> float:
        """Get the current of a battery sensor."""
        if identifier != 0:
            raise ValueError(f"invalid battery sensor identifier {identifier!r}; "
                             f"the only valid identifier is 0")
        current, voltage = struct.unpack("<II", self._read(CMD_READ_BATTERY))
        return cast(int, current) / 1000  # convert milliamps to amps

    def get_led_state(self, board: Board, identifier: int) -> bool:
        """Get the state of an LED."""
        return self._led_states[identifier]

    def set_led_state(self, board: Board, identifier: int, state: bool) -> None:
        """Set the state of an LED."""
        cmds = {0: CMD_WRITE_RUNLED, 1: CMD_WRITE_ERRORLED}
        try:
            cmd = cmds[identifier]
        except KeyError:
            raise ValueError(f"invalid LED identifier {identifier!r}; valid identifiers "
                             f"are 0 (run LED) and 1 (error LED)") from None
        self._write(cmd, int(state))
        self._led_states[identifier] = state
