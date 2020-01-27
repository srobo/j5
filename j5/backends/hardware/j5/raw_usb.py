"""
Abstract hardware backend implemention provided by j5 for Raw USB communication.

This has been written to reduce code duplication between backends for boards that
communicate very similarly. It has been written such that it could potentially be
distributed separately in the future, to remove the PyUSB dependency from the j5 core.
"""

from abc import abstractmethod
from threading import Lock
from typing import NamedTuple, Optional, Set, Union

import usb

from j5.backends import Backend, BackendMeta, CommunicationError
from j5.boards import Board

# Stop the library from closing the USB connections before make_safe is called.
usb._objfinalizer._AutoFinalizedObjectBase._do_finalize_object = (  # type: ignore
    lambda x: None
)


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


class USBCommunicationError(CommunicationError):
    """An error occurred during USB communication."""

    def __init__(self, usb_error: usb.core.USBError) -> None:
        self.usb_error = usb_error
        self.message = usb_error.strerror
        super().__init__(self.message)


class RawUSBHardwareBackend(Backend, metaclass=BackendMeta):
    """An abstract class for creating backends that use Raw USB communication."""

    _usb_device: usb.core.Device

    def __init__(self) -> None:
        self._lock = Lock()

    @classmethod
    @abstractmethod
    def discover(cls) -> Set[Board]:
        """Discover boards that this backend can control."""
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        raise NotImplementedError  # pragma: no cover

    @property
    def serial(self) -> str:
        """The serial number reported by the board."""
        with self._lock:
            try:
                return self._usb_device.serial_number
            except usb.core.USBError as e:
                raise USBCommunicationError(e) from e

    def __del__(self) -> None:
        """Clean up device on destruction of object."""
        # Note: we do not obtain the lock here.
        # This is because we want to close the device ASAP in an emergency.
        try:
            usb.util.dispose_resources(self._usb_device)
        except usb.core.USBError as e:
            raise USBCommunicationError(e) from e

    def _read(self, command: ReadCommand) -> bytes:
        """Read bytes from the USB control endpoint."""
        with self._lock:
            try:
                return self._usb_device.ctrl_transfer(
                    0x80,
                    64,
                    wValue=0,
                    wIndex=command.code,
                    data_or_wLength=command.data_len,
                )
            except usb.core.USBError as e:
                raise USBCommunicationError(e) from e

    def _write(self, command: WriteCommand, param: Union[int, bytes]) -> None:
        """Write bytes to the USB control endpoint."""
        req_val: int = 0
        req_data: bytes = b""
        if isinstance(param, int):
            req_val = param
        else:
            req_data = param

        with self._lock:
            try:
                self._usb_device.ctrl_transfer(
                    0x00,
                    64,
                    wValue=req_val,
                    wIndex=command.code,
                    data_or_wLength=req_data,
                )
            except usb.core.USBError as e:
                raise USBCommunicationError(e) from e
