"""Test the full stack."""

from j5.boards.j5 import DemoBoard
from j5.backends.dummy.env import DummyEnvironment


class Robot:

    def __init__(self):

        self._env = DummyEnvironment
        self.demo_board = DemoBoard(DummyEnvironment)
