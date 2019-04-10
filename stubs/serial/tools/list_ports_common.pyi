"""Type stubs for serial.tools.list_ports_common."""

class ListPortInfo:
    """Info collection base class for serial ports"""

    device: str
    description: str
    vid: int
    pid: int
    serial_number: str
    manufacturer: str
    product: str


    def __init__(self, device: str, skip_link_detection: bool = False) -> None: ...
