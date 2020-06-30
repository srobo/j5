Abstractions
============

`j5` utilises a number of abstractions to enable similar APIs across platforms and hardware. This page explains design decisions behind the major abstractions and how to use them correctly.

Component
---------

Definition
~~~~~~~~~~

A component is the smallest logical part of some hardware.

A component will have the same basic functionality no matter what hardware it is on. For example, an LED is still an LED, no matter whether it is on an Arduino, or the control panel of a jumbo jet; it still can be turned on and off.

Implementation
~~~~~~~~~~~~~~

A component is implemented by sub-classing the :class:`j5.components.Component`.

It is uniquely identified on a particular :class:`j5.boards.Board` by an integer, which is usually passed into the constructor. 

Every component should have a reference to a :class:`j5.backends.Backend`, that implements the relevant :class:`j5.components.Interface`.

.. literalinclude:: ../../j5/components/led.py
    :language: python
    :linenos:
    :lines: 23-48


Interface
---------

Board
-----

Backend
-------
