Quick Start Guide
=================

Firstly, you will need to ensure that you have `installed j5`_. You will also need a
working knowledge of Python 3.

.. _`installed j5`: installation

Your First Robot
----------------

The recommended way to use `j5` is to first define what the structure of your robot looks like.

You will probably want

.. code-block:: python

    from j5 import BaseRobot

    class MyRobot(BaseRobot):
        """My Basic Robot definition."""

    r = MyRobot()

Adding Boards
-------------

To give you robot some functionality, you will need to define what boards are available on your robot.

.. code-block:: python

    from j5 import BaseRobot
    from j5.backends.console import ConsoleEnvironment

    from vendor.boards import PowerBoard, MotorBoard

    class MyRobot(BaseRobot):
        """A robot with a few boards."""

        def __init__(self):
            self._power_boards = BoardGroup(PowerBoard, ConsoleEnvironment.get_backend(PowerBoard))
            self.power_board = self.power_boards.singular()  # Restrict to exactly one board.

            self.motor_boards = BoardGroup(MotorBoard, ConsoleEnvironment.get_backend(MotorBoard))

    r = MyRobot()

    print(f"Found Power Board: {r.power_board.serial}")
    print(f"Power Board Firmware: {r.power_board.firmware_version}")

    # Access a board specific attribute
    print(f"Power Board Manufacturing ID: {r.power_board.manufacture_id}")

    # Access a board specific function
    r.power_board.power_on()

    print(f"Found {len(r.motor_boards)} Motor Board(s):")

    # Iterate over the boards in a board group
    for board in r.motor_boards:
        print(f" - {board.serial} - Version {board.firmware_version}")

    # Access board by serial number
    r.motor_boards["218312"].make_safe()

In order to add some boards to your robot, you will need to define the ``BoardGroup`` for your board.
A ``BoardGroup`` is a group of boards attached to your robot. A ``BoardGroup`` can contain 0 or more of
the specified board. You can also call ``singular()`` on your ``BoardGroup``, and it will throw an error
if there is not exactly one board of that type connected.

If your robot does not consistent of a modular kit, and is entirely contained within one unit, you do not
have to use the board separation, you can instead directly expose components to the use.

Note that whilst we can iterate over a ``BoardGroup`` and access a board in a ``BoardGroup`` by serial, we
cannot access a board using array notation.

Using Components
----------------

Whilst it is useful to be able to access attributes and functions that are specific to a board, the real power
of `j5` is found when you access components and functionality on those boards. `j5` has defined a consistent
interface for those components, even if they are on separate devices.

.. code-block:: python

    class MyRobot(BaseRobot):
        """A robot with a few boards."""

        def __init__(self):
            self._power_boards = BoardGroup(PowerBoard, ConsoleEnvironment.get_backend(PowerBoard))
            self.power_board = self.power_boards.singular()  # Restrict to exactly one board.

            # Expose just a component to the user.
            self.big_led = self.power_board.leds[0]

    r = MyRobot()

    # Ensure all LEDs on the power board are off.

    for led in r.power_board.leds:
        led.state = False

    # Turn on the big LED
    r.big_led.state = True

The usual method to access components is to use the definition on the board. It is also possible to expose a
component, or even a single attribute on a component as a top level attribute of your Robot object.
