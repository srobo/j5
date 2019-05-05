"""The hardware Environment."""

from j5.backends import Environment

HardwareEnvironment = Environment("HardwareEnvironment")


class NotSupportedByHardwareError(Exception):
    """The hardware does not support that functionality."""
