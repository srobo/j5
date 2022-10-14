"""Abstract hardware backend implementation provided by j5 for serial comms."""
import logging
from abc import abstractmethod
from datetime import timedelta
from typing import List, Optional, Set, Type

from serial import Serial, SerialException, SerialTimeoutException
from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo

from j5.backends import Backend, BackendMeta, CommunicationError
from j5.boards import Board


class SerialHardwareBackend(Backend, metaclass=BackendMeta):
    """An abstract class for creating backends that use USB serial communication."""

    DEFAULT_TIMEOUT: timedelta = timedelta(milliseconds=250)

    def __init__(
            self,
            serial_port: str,
            *,
            baud: int = 115200,
            timeout: timedelta = DEFAULT_TIMEOUT,
    ) -> None:
        timeout_secs = timeout / timedelta(seconds=1)
        serial_class = self.get_serial_class()
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

    @classmethod
    def get_comports(cls) -> List[ListPortInfo]:
        """
        Get comports.

        :returns: List of available serial ports.
        """
        return comports()

    @property
    @abstractmethod
    def firmware_version(self) -> Optional[str]:
        """
        The firmware version reported by the board.

        :returns: firmware version reported by the board, if any.
        """
        raise NotImplementedError  # pragma: no cover

    def get_serial_class(self) -> Type[Serial]:
        """
        Get the serial class.

        :returns: PySerial class to use for serial comms.
        """
        return Serial

    def read_serial_line(self, empty: bool = False) -> str:
        """
        Read a line from the serial interface.

        :param empty: Allow empty line.
        :returns: line read from serial port.
        :raises CommunicationError: serial error whilst reading line.
        :raises UnicodeDecodeError: serial returned invalid unicode.
        """
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

        try:
            ldata = bdata.decode('utf-8')
        except UnicodeDecodeError as e:
            if empty:
                logging.getLogger(__file__).error(f"{e} in {bdata!r}")
                return ''
            raise
        return ldata.rstrip()

    def read_serial_chars(self, size: int = 1) -> str:
        """
        Read chars from the serial interface.

        :param size: number of bytes to read.
        :returns: decoded characters
        :raises ValueError: insufficient data in serial buffer.
        :raises CommunicationError: an error occurred during serial comms.
        """
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
