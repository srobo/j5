"""Test the full stack."""

import pytest

from j5 import BaseRobot
from j5.backends.dummy.env import DummyEnvironment
from j5.base_robot import UnableToObtainLock
from j5.boards.j5 import DemoBoard


class Robot(BaseRobot):
    """A robot."""

    def __init__(self):
        self._env = DummyEnvironment
        self.demo_board = DemoBoard("0000", DummyEnvironment)


def test_led():
    """Test that I can turn on the LEDs."""
    r = Robot()

    for led in r.demo_board.leds:
        led.state = True


def test_robot_lock():
    """Test that we cannot have more than one Robot object."""
    r1 = Robot()

    assert r1._lock

    with pytest.raises(UnableToObtainLock):
        Robot()
