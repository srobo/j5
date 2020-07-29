"""Abstract hardware backend implementation provided by j5 for serial comms."""
from abc import abstractmethod
from datetime import timedelta
from typing import Optional, Set, Type, cast

from serial import Serial, SerialException, SerialTimeoutException
from typing_extensions import Protocol

from j5.backends import Backend, BackendMeta, CommunicationError
from j5.boards import Board


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
        ...  # pragma: nocover

    def close(self) -> None:
        """Close the connection."""
        ...  # pragma: nocover

    def flush(self) -> None:
        """Flush all pending write operations."""
        ...  # pragma: nocover

    def readline(self) -> bytes:
        """Read a line from the serial port."""
        ...  # pragma: nocover

    @property
    @abstractmethod
    def in_waiting(self) -> int:
        """Return the number of characters currently in the input buffer."""
        ...  # pragma: nocover

    def read(self, size: int = 1) -> bytes:
        """Read size bytes from the serial port."""
        ...  # pragma: nocover

    def write(self, data: bytes) -> int:
        """Write data to the serial port."""
        ...  # pragma: nocover


class SerialHardwareBackend(Backend, metaclass=BackendMeta):
    """An abstract class for creating backends that use USB serial communication."""

    DEFAULT_TIMEOUT: timedelta = timedelta(milliseconds=250)

    def __init__(
            self,
            serial_port: str,
            *,
            serial_class: Type[Seriallike] = cast(Type[Seriallike], Serial),  # noqa: B008
            baud: int = 115200,
            timeout: timedelta = DEFAULT_TIMEOUT,
    ) -> None:
        timeout_secs = timeout / timedelta(seconds=1)
        try:
            self._serial = serial_class(
                port=serial_port,
                baudrate=baud,
                timeout=timeout_secs,
            )
        except SerialTimeoutException as e:
            raise CommunicationError(f"Serial Timeout Error: {e}") from e
        except SerialException as e:
            raise CommunicationError(f"Serial Error: {e}") from e

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

    def read_serial_line(self, empty: bool = False) -> str:
        """Read a line from the serial interface."""
        try:
            bdata = self._serial.readline()
        except SerialTimeoutException as e:
            raise CommunicationError(f"Serial Timeout Error: {e}") from e
        except SerialException as e:
            raise CommunicationError(f"Serial Error: {e}") from e

        if len(bdata) == 0:
            if empty:
                return ""
            raise CommunicationError(
                "No response from board. "
                "Is it correctly powered?",
            )

        ldata = bdata.decode('utf-8')
        return ldata.rstrip()

    def read_serial_chars(self, size: int = 1) -> str:
        """Read size bytes from the serial interface."""
        if size > self._serial.in_waiting:
            raise ValueError(f"Tried to read {size} bytes from the serial buffer, "
                             f"only {self._serial.in_waiting} were available.")

        try:
            bdata = self._serial.read(size)
        except SerialTimeoutException as e:
            raise CommunicationError(f"Serial Timeout Error: {e}") from e
        except SerialException as e:
            raise CommunicationError(f"Serial Error: {e}") from e

        if len(bdata) != size:
            raise CommunicationError(
                f"Expected to receive {size} chars, got {len(bdata)} instead.",
            )

        ldata = bdata.decode('utf-8')
        return ldata.rstrip()
