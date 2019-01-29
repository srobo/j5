"""Test the DemoBoardDummyBackend."""

from j5.backends.dummy.demo import DemoBoardDummyBackend


def test_set_led():
    """Test that the backend can set the state of an LED."""
    demo = DemoBoardDummyBackend()
    demo.set_led_state(None, 0, True)


def test_get_led():
    """Test that this backend can get the state of an LED."""
    demo = DemoBoardDummyBackend()
    demo.get_led_state(None, 0)
