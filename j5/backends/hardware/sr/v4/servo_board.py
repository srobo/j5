"""Hardware Backend for the SR V4 Servo Board."""

import struct
from typing import Callable, List, Set, cast

import usb

from j5.backends import CommunicationError
from j5.backends.hardware.env import NotSupportedByHardwareError
from j5.backends.hardware.j5.raw_usb import (
    RawUSBHardwareBackend,
    ReadCommand,
    USBCommunicationError,
    WriteCommand,
)
from j5.boards import Board
from j5.boards.sr.v4 import ServoBoard
from j5.components.servo import ServoInterface, ServoPosition

CMD_READ_FWVER = ReadCommand(9, 4)

CMD_WRITE_SET_SERVO = [
    WriteCommand(i)
    for i in range(0, 12)
]
CMD_WRITE_INIT = WriteCommand(12)


class SRV4ServoBoardHardwareBackend(
    ServoInterface,
    RawUSBHardwareBackend,
):
    """The hardware implementaton of the SR v4 Servo Board."""

    board = ServoBoard

    @classmethod
    def discover(cls, find: Callable = usb.core.find) -> Set[Board]:
        """Discover boards that this backend can control."""
        boards: Set[Board] = set()
        try:
            device_list = find(idVendor=0x1bda, idProduct=0x0011, find_all=True)
        except usb.core.USBError as e:
            raise USBCommunicationError(e) from e

        for device in device_list:
            backend = cls(device)
            board = ServoBoard(backend.serial, backend)
            boards.add(cast(Board, board))
        return boards

    def __init__(self, usb_device: usb.core.Device) -> None:
        super().__init__()

        self._usb_device = usb_device

        self.check_firmware_version_supported()

        self._positions: List[float] = [0.0] * 12

        # Initialise servos.
        self._write(CMD_WRITE_INIT, b"")

        for s in range(0, 12):
            self.set_servo_position(s, 0.0)

    @property
    def firmware_version(self) -> str:
        """The firmware version reported by the board."""
        try:
            version, = struct.unpack("<I", self._read(CMD_READ_FWVER))
            return str(cast(int, version))
        except USBCommunicationError as e:
            if e.usb_error.errno in [5, 110]:  # "Input/Output", "operation timed out"
                raise CommunicationError(
                    f"{e}; are you sure the servo board"
                    f" is being correctly powered?",
                )
            raise

    def check_firmware_version_supported(self) -> None:
        """Raises an exception if the firmware version is not supported."""
        v = self.firmware_version
        if v != "2":
            raise NotImplementedError(f"Servo Board ({self.serial}) is running firmware "
                                      f"version {v}, but only version 2 is supported")

    def get_servo_position(self, identifier: int) -> ServoPosition:
        """
        Get the position of a servo.

        Currently reads back the last known position as we cannot read from the hardware.
        """
        if identifier not in range(0, 12) or not isinstance(identifier, int):
            raise ValueError("Only integers 0 - 11 are valid servo identifiers.")
        return self._positions[identifier]

    def set_servo_position(self, identifier: int, position: ServoPosition) -> None:
        """Set the position of a servo."""
        if identifier not in range(0, 12) or not isinstance(identifier, int):
            raise ValueError("Only integers 0 - 11 are valid servo identifiers.")

        if position is None:
            raise NotSupportedByHardwareError(
                f"{self.board.name} does not support unpowered servos.",
            )
        elif position < -1 or position > 1:
            raise ValueError("Only numbers between -1 and 1 are valid servo positions.")

        self._positions[identifier] = position
        value = round(position * 100)
        self._write(CMD_WRITE_SET_SERVO[identifier], value)
