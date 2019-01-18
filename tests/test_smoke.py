"""No tests at the moment."""

from j5.boards.j5 import DemoBoard
from j5 import BoardGroup
from j5.backends.dummy import DummyBackendGroup


def test_if_we_can_make_a_robot():
    """Test thingshodgihsdfghsoidfhgiodsf"""

    class Robot:

        def __init__(self):

            self._backend_group = DummyBackendGroup()

            self.demo_boards = BoardGroup(DemoBoard, self._backend_group)

    r = Robot()

    for d in r.demo_boards:
        for l in d.leds:
            l.state = True
