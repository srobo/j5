"""Test the full stack."""

import pytest, socket

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
    
    r1._obtain_lock()  # Check we can re-obtain the lock on the same object.

    assert isinstance(r1._lock, socket.socket)
    assert r1.lock.getsockname()[1] == 10653

    with pytest.raises(UnableToObtainLock):
        Robot()
