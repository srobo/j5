"""Dummy Backends for the demo boards."""

from j5.backends import Backend
from j5.components import LEDInterface


class DemoBoardDummyBackend(LEDInterface, Backend):
    """The dummy implementation of the DemoBoard."""

    def set_led_state(self, identifier: int, state: bool) -> None:
        """Set the state of an LED."""
        print("Set LED {} to {}".format(str(identifier), str(state)))

    def get_led_state(self, identifier: int) -> bool:
        """Set the state of an LED."""
        return False
