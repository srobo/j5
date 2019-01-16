"""Dummy Backends for the demo boards."""

from j5.backends import Backend
from j5.components import LEDInterface


class DemoBoardDummyBackend(LEDInterface, Backend):
    """The dummy implementation of the DemoBoard."""
