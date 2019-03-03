"""
Type stubs for usb.core

Note that stubs are only written for the parts that we use.
"""

from typing import Generator, Optional, Union

class Configuration:
    def ___init__(self, device: Device, configuration: int = 0) -> None: ...


class Device:
    def serial_number(self) -> str: ...
    def product(self) -> str: ...
    def manufacturer(self) -> str: ...

    def set_configuration(self, configuration: Optional[Configuration] = None) -> None: ...
    def get_active_configuration(self) -> Configuration: ...

    def reset(self) -> None : ...

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
    strerror: str

def find(
        find_all: bool = False,
        idVendor: Optional[int] = None,
        idProduct: Optional[int] = None,
) -> Generator[Device, None, None]: ...