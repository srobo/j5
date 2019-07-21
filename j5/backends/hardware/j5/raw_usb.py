"""
Abstract hardware backend implemention provided by j5 for Raw USB communication.

This has been written to reduce code duplication between backends for boards that
communicate very similarly. It has been written such that it could potentially be
distributed separately in the future, to remove the PyUSB dependency from the j5 core.
"""

from abc import abstractmethod
from functools import wraps
from typing import Callable, NamedTuple, Optional, Set, TypeVar, Union

import usb

from j5.backends import BackendMeta, CommunicationError, Environment
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
        super().__init__(usb_error.strerror)


RT = TypeVar('RT')


def handle_usb_error(func: Callable[..., RT]) -> Callable[..., RT]:  # type: ignore
    """
    Wrap functions that use usb1 and give friendly errors.

    The exceptions from PyUSB are hard to find in documentation or code and are confusing
    to users. This decorator catches the USBErrors and throws a friendlier exception that
    can also be caught more easily.
    """
    @wraps(func)
    def catch_exceptions(*args, **kwargs):  # type: ignore
        try:
            return func(*args, **kwargs)
        except usb.core.USBError as e:
            raise USBCommunicationError(e)
    return catch_exceptions


class RawUSBHardwareBackend(metaclass=BackendMeta):
    """An abstract class for creating backends that use Raw USB communication."""

    _usb_device: usb.core.Device

    @classmethod
    @abstractmethod
    def discover(cls) -> Set[Board]:
        """Discover boards that this backend can control."""
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def environment(self) -> 'Environment':
        """Environment the backend belongs too."""
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        raise NotImplementedError  # pragma: no cover

    @property  # type: ignore # https://github.com/python/mypy/issues/1362
    @handle_usb_error
    def serial(self) -> str:
        """The serial number reported by the board."""
        # https://github.com/python/mypy/issues/1362
        return self._usb_device.serial_number

    @handle_usb_error
    def __del__(self) -> None:
        """Clean up device on destruction of object."""
        usb.util.dispose_resources(self._usb_device)

    @handle_usb_error
    def _read(self, command: ReadCommand) -> bytes:
        return self._usb_device.ctrl_transfer(
            0x80,
            64,
            wValue=0,
            wIndex=command.code,
            data_or_wLength=command.data_len,
        )

    @handle_usb_error
    def _write(self, command: WriteCommand, param: Union[int, bytes]) -> None:
        req_val: int = 0
        req_data: bytes = b""
        if isinstance(param, int):
            req_val = param
        else:
            req_data = param

        self._usb_device.ctrl_transfer(
            0x00,
            64,
            wValue=req_val,
            wIndex=command.code,
            data_or_wLength=req_data,
        )
