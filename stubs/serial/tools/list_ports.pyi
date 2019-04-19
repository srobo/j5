"""Type stubs for serial.tools.list_ports."""

from typing import List

from .list_ports_common import ListPortInfo

def comports(include_links: bool = False) -> List[ListPortInfo]: ...