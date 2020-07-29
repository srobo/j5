Quick Start Guide
=================

Firstly, you will need to ensure that you have `installed j5`_. You will also need a
working knowledge of Python 3.

.. _`installed j5`: installation

Your First Robot
----------------

The recommended way to use `j5` is to first define what the structure of your robot looks like.

You will probably want

.. literalinclude:: ../_code/qs_first_robot.py

Adding Boards
-------------

To give you robot some functionality, you will need to define what boards are available on your robot.

.. literalinclude:: ../_code/qs_adding_boards.py

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

.. literalinclude:: ../_code/qs_using_components.py

The usual method to access components is to use the definition on the board. It is also possible to expose a
component, or even a single attribute on a component as a top level attribute of your Robot object.
