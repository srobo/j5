"""
Type stubs for usb.core

Note that stubs are only written for the parts that we use.
"""

from .core import Device

def dispose_resources(device: Device) -> None: ...
