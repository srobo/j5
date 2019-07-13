"""A class that mocks serial.Serial."""

from typing import Optional


class MockSerial:
    """This class mocks the behaviour of serial.Serial."""

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
        self._receive_buffer: bytes = b""
        self._send_buffer: bytes = b""
        self.port = port

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
        """Ensure all data written to the serial port has been sent."""
        pass

    def read(self, size: int = 1) -> bytes:
        """Read size bytes from the input buffer."""
        assert len(self._receive_buffer) >= size

        data = self._receive_buffer[:size]
        self._receive_buffer = self._receive_buffer[size:]
        return data

    def readline(self) -> bytes:
        """Read up to a newline on the serial port."""
        try:
            pos = self._receive_buffer.index(b'\n')
        except ValueError:
            return b''
        return self.read(pos + 1)

    def write(self, data: bytes) -> int:
        """Write the data to the serial port."""
        self._send_buffer += data

        # We only end up returning data once, check for that here.
        if data == b'\x01':  # Version Command
            self.append_received_data(b'MCV4B:3', newline=True)

        return len(data)

    # Functions for helping us mock.

    def append_received_data(self, data: bytes, newline: bool = False) -> None:
        """Append some data to the receive buffer."""
        self._receive_buffer += data
        if newline:
            self._receive_buffer += b'\n'

    def check_sent_data(self, data: bytes) -> None:
        """Check that the given data is what was written to the serial port."""
        assert data == self._send_buffer, f"{data!r} != {self._send_buffer!r}"
        self._send_buffer = b""
