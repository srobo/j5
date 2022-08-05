"""The hardware Environment."""


from j5.exceptions import j5Exception


class NotSupportedByHardwareError(j5Exception):
    """The hardware does not support that functionality."""
