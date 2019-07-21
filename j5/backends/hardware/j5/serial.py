"""Abstract hardware backend implementation provided by j5 for serial comms."""
from abc import abstractmethod
from datetime import timedelta
from functools import wraps
from typing import TYPE_CHECKING, Callable, Optional, Set, Type, TypeVar

from serial import Serial, SerialException, SerialTimeoutException

from j5.backends import BackendMeta, CommunicationError, Environment
from j5.boards import Board

RT = TypeVar("RT")  # pragma: nocover

if TYPE_CHECKING:
    from typing_extensions import Protocol
else:
    class Protocol:
        """Dummy class since typing_extensions is not available at runtime."""

        pass


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


class Seriallike(Protocol):
    """
    Something that walks like a Serial and quacks like a Serial.

    This is used instead of hardcoding the Serial class to allow it to be mocked out.
    """

    def __init__(self,
                 port: Optional[str] = None,
                 baudrate: int = 9600,
                 bytesize: int = 8,
                 parity: str = 'N',
                 stopbits: float = 1,
                 timeout: Optional[float] = None):
        ...

    def close(self) -> None:
        """Close the connection."""
        ...

    def flush(self) -> None:
        """Flush all pending write operations."""
        ...

    def readline(self) -> bytes:
        """Read a line from the serial port."""
        ...

    def write(self, data: bytes) -> int:
        """Write data to the serial port."""
        ...


class SerialHardwareBackend(metaclass=BackendMeta):
    """An abstract class for creating backends that use USB serial communication."""

    @handle_serial_error
    def __init__(
            self,
            serial_port: str,
            serial_class: Type[Seriallike] = Serial,
            baud: int = 115200,
            timeout: timedelta = timedelta(milliseconds=250),
    ) -> None:
        timeout_secs = timeout / timedelta(seconds=1)
        self._serial = serial_class(
            port=serial_port,
            baudrate=baud,
            timeout=timeout_secs,
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
                "No response from board. "
                "Is it correctly powered?",
            )

        ldata = bdata.decode('utf-8')
        return ldata.rstrip()
