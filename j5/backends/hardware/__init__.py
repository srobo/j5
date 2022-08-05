"""Backends for the hardware environment."""

from j5.backends import CommunicationError

from .env import NotSupportedByHardwareError


class DeviceMissingSerialNumberError(CommunicationError):
    """The device is missing a serial number."""


__all__ = [
    "DeviceMissingSerialNumberError",
    "NotSupportedByHardwareError",
]
