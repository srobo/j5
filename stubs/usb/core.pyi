"""
Type stubs for usb.core

Note that stubs are only written for the parts that we use.
"""

from typing import Generator, Optional, Tuple, Union


class Device:

    _langids: Tuple[int, ...]

    @property
    def serial_number(self) -> str: ...

    def ctrl_transfer(
            self,
            bmRequestType: int,
            bRequest: int,
            wValue: int = 0,
            wIndex:int = 0,
            data_or_wLength: Optional[Union[int, bytes]] = None,
            timeout: Optional[int] = None,
    ) -> bytes: ...

class USBError(Exception):
    errno: int
    strerror: str

    def __init__(
        self,
        strerror: str,
        error_code: Optional[int] = None,
        errno: Optional[int] = None,
    ): ...

def find(
        find_all: bool = False,
        idVendor: Optional[int] = None,
        idProduct: Optional[int] = None,
) -> Generator[Device, None, None]: ...
