"""
Abstract hardware backend implemention provided by j5 for Raw USB communication.

This has been written to reduce code duplication between backends for boards that
communicate very similarly. It has been written such that it could potentially be
distributed separately in the future, to remove the PyUSB dependency from the j5 core.
"""

from .raw_usb import (
    RawUSBHardwareBackend,
    ReadCommand,
    USBCommunicationError,
    WriteCommand,
    handle_usb_error,
)

__all__ = [
    "RawUSBHardwareBackend",
    "ReadCommand",
    "USBCommunicationError",
    "WriteCommand",
    "handle_usb_error",
]
