"""Test the full stack."""

from j5 import BaseRobot
from j5.boards.j5 import DemoBoard
from j5.backends.dummy.env import DummyEnvironment


class Robot(BaseRobot):

    def __init__(self):
        self._env = DummyEnvironment
        self.demo_board = DemoBoard("0000", DummyEnvironment)


def test_led():
    """Test that I can turn on the LEDs."""

    r = Robot()

    for led in r.demo_board.leds:
        led.state = True
