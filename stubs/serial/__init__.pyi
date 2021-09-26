"""
Type stubs for PySerial.

Note that stubs are only written for the parts that we use.
"""

from typing import Optional

class SerialException(IOError): ...
class SerialTimeoutException(SerialException): ...


class Serial:

    def __init__(self,
         port: Optional[str] = None,
         baudrate: int = 9600,
         bytesize: int = 8,
         parity: str = 'N',
         stopbits: float = 1,
         timeout: Optional[float] = None,
         ): ...

    def close(self) -> None: ...
    def flush(self) -> None: ...

    def read(self, size: int = 1) -> bytes: ...
    def readline(self) -> bytes: ...
    def write(self, data: bytes) -> int: ...

    @property
    def in_waiting(self) -> int: ...