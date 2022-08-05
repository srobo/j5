"""Type stubs for serial.tools.list_ports_common."""
from typing import Optional

class ListPortInfo:
    """Info collection base class for serial ports"""

    device: str
    vid: Optional[int]
    pid: Optional[int]
    serial_number: Optional[str]
    manufacturer: Optional[str]
    product: Optional[str]


    def __init__(self, device: str, skip_link_detection: bool = False) -> None: ...
    def usb_info(self) -> str: ...
