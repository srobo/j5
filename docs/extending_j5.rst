Extending j5
============

`j5` utilises a number of abstractions to enable similar APIs across platforms and hardware. This page explains design decisions behind the major abstractions and how to use them correctly.

Component
---------

A component is the smallest logical part of some hardware.

A component will have the same basic functionality no matter what hardware it is on. For example, an LED is still an LED, no matter whether it is on an Arduino, or the control panel of a jumbo jet; it still can be turned on and off.

The component should expose a user-friendly API, attempting to be consistent with other components where possible.

Validation of user input should be done in the component.

Implementation
~~~~~~~~~~~~~~

A component is implemented by sub-classing the :class:`j5.components.Component`.

It is uniquely identified on a particular :class:`j5.boards.Board` by an integer, which is usually passed into the constructor. 

Every instance of a component should have a reference to a :class:`j5.backends.Backend`, that implements the relevant :class:`j5.components.Interface`.

The relevant :class:`j5.components.Interface` should also be defined.

.. literalinclude:: ../j5/components/led.py
    :language: python
    :linenos:
    :lines: 23-48


Interface
---------

An interface defines the low-level methods that are required to control a given component.

Implementation
~~~~~~~~~~~~~~

An interface should sub-class :class:`j5.components.Interface`.

The interface class should contain abstract methods required to control the component.

.. literalinclude:: ../j5/components/led.py
    :language: python
    :linenos:
    :lines: 9-20

Board
-----

A Board is a class that exposes a group of components, used to represent a physical board in a robotics kit.

The Board class should not directly interact with any hardware, instead making calls to the Backend class where necessary, and preferably diverting interaction through the component classes where possible.

Implementation
~~~~~~~~~~~~~~

An interface should sub-class :class:`j5.boards.Board`.

It will need to implement a number of abstract functions on that class.

Components should be created in the constructor, and should be made available to the user through properties. Care should be taken to ensure that users cannot accidentally override components.

A backend should also be passed to the board in the constructor, usually done in :meth:`j5.backends.Backend.discover`

A notable method that should be implemented is :meth:`j5.boards.Board.make_safe`, which should call the appropriate methods on the components to ensure that the board is safe in the event of something going wrong.

.. literalinclude:: ../j5/boards/sr/v4/motor_board.py
    :language: python
    :linenos:
    :lines: 14-52

Backend
-------

A backend implements all of the interfaces required to control a board.

A backend also contains a method that can discover boards.

Multiple backends can be implemented for one board, but a backend can only support one board. This could be used for implementing a simulated version of a board, in addition to the hardware implementation.

Backends can also validate is data is suitable for them, and throw an error if not; for example :class:`j5.backends.hardware.env.NotSupportedByHardwareError`.

Implementation
~~~~~~~~~~~~~~

.. literalinclude:: ../j5/backends/console/sr/v4/motor_board.py
    :language: python
    :linenos:
    :lines: 12-64
