"""A class that mocks serial.Serial."""

from typing import Optional


class MockSerial:
    """This class mocks the behaviour of serial.Serial."""

    initial_expects = b""
    expected_baudrate = 9600

    def __init__(self,
                 port: Optional[str] = None,
                 baudrate: int = 9600,
                 bytesize: int = 8,
                 parity: str = 'N',
                 stopbits: float = 1,
                 timeout: Optional[float] = None,
                 ):
        self._is_open: bool = True
        self._buffer: bytes = b''
        self.port = port
        self._expects = self.initial_expects

        assert baudrate == self.expected_baudrate
        assert bytesize == 8
        assert parity == 'N'
        assert stopbits == 1
        assert timeout is not None
        assert 0.1 <= timeout <= 0.3  # Acceptable range of timeouts

    def close(self) -> None:
        """Close the serial port."""
        assert self._is_open  # Check the port is open first.
        self._is_open = False

    def flush(self) -> None:
        """Flush the buffer on the serial port."""
        self._buffer = b''

    def read(self, size: int = 1) -> bytes:
        """Read size bytes from the input buffer."""
        assert len(self._buffer) >= size

        data = self._buffer[:size]
        self._buffer = self._buffer[size:]
        return data

    def readline(self) -> bytes:
        """Read up to a newline on the serial port."""
        try:
            pos = self._buffer.index(b'\n')
        except ValueError:
            return b''
        return self.read(pos)

    def write(self, data: bytes) -> int:
        """Write the data to the serial port."""
        self.check_expects(data)

        # We only end up returning data once, check for that here.
        if data == b'\x01':  # Version Command
            self.buffer_append(b'MCV4B:3', newline=True)

        return len(data)

    # Functions for helping us mock.

    def buffer_append(self, data: bytes, newline: bool = False) -> None:
        """Append some data to the receive buffer."""
        self._buffer += data
        if newline:
            self._buffer += b'\n'

    def expects_prepend(self, data: bytes) -> None:
        """Prepend some bytes to the output buffer that we expect to see."""
        self._expects = data + self._expects

    def check_expects(self, data: bytes) -> None:
        """Check that the given data is what we expect to see on the output buffer."""
        length = len(data)
        assert data == self._expects[:length]
        self._expects = self._expects[length:]
