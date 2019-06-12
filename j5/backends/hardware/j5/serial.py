"""Abstract hardware backend implementation provided by j5 for serial comms."""
from abc import abstractmethod
from functools import wraps
from typing import Callable, Optional, Set, Type, TypeVar

from serial import Serial, SerialException, SerialTimeoutException

from j5.backends import BackendMeta, CommunicationError, Environment
from j5.boards import Board

RT = TypeVar("RT")  # pragma: nocover


def handle_serial_error(func: Callable[..., RT]) -> Callable[..., RT]:  # type: ignore
    """
    Wrap functions that use the serial port, and rethrow the errors.

    This is a decorator that should be used to wrap any functions that call the serial
    interface. It will catch and rethrow the errors as a CommunicationError, so that it
    is more explicit what is going wrong.
    """
    @wraps(func)
    def catch_exceptions(*args, **kwargs):  # type: ignore
        try:
            return func(*args, **kwargs)
        except SerialTimeoutException as e:
            raise CommunicationError(f"Serial Timeout Error: {e}")
        except SerialException as e:
            raise CommunicationError(f"Serial Error: {e}")
    return catch_exceptions


class SerialHardwareBackend(metaclass=BackendMeta):
    """An abstract class for creating backends that use Raw USB communication."""

    @handle_serial_error
    def __init__(
            self,
            serial_port: str,
            serial_class: Type[Serial] = Serial,
            baud: int = 115200,
            timeout: float = 0.25,
    ) -> None:
        self._serial = serial_class(
            port=serial_port,
            baudrate=baud,
            timeout=timeout,
        )

    @classmethod
    @abstractmethod
    def discover(cls) -> Set[Board]:
        """Discover boards that this backend can control."""
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def environment(self) -> Environment:
        """Environment the backend belongs too."""
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def firmware_version(self) -> Optional[str]:
        """The firmware version of the board."""
        raise NotImplementedError  # pragma: no cover

    @handle_serial_error
    def read_serial_line(self, empty: bool = False) -> str:
        """Read a line from the serial interface."""
        bdata = self._serial.readline()

        if len(bdata) == 0:
            if empty:
                return ""
            raise CommunicationError(
                "Unable to communicate with motor board. ",
                "Is it correctly powered?",
            )

        ldata = bdata.decode('utf-8')
        return ldata.rstrip()
