"""Test the full stack."""

import socket

import pytest

from j5 import BaseRobot
from j5.backends import Environment
from j5.base_robot import UnableToObtainLock

TestEnvironment = Environment("TestEnvironment")


class Robot(BaseRobot):
    """A robot."""

    def __init__(self, debug: bool = False) -> None:
        self._env = TestEnvironment
        self.debug = debug


def test_robot_lock() -> None:
    """Test that we cannot have more than one Robot object."""
    r1 = Robot()

    r1._obtain_lock()  # Check we can re-obtain the lock on the same object.

    assert isinstance(r1._lock, socket.socket)
    assert r1._lock.getsockname()[1] == 10653

    with pytest.raises(UnableToObtainLock):
        Robot()


def test_robot_with_args() -> None:
    """Test that a Robot can accept additional args."""
    r = Robot(debug=True)

    assert r.debug
