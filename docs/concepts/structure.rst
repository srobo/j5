Class Structure
===============

`j5` has a somewhat abstract nature due to the number of things that it can support. It is not necessary for
the average developer or student to understand everything that is going on here.

Basic Structure
---------------

The following diagram shows the main classes at a very basic level, with their inheritance.

.. graphviz::

   digraph {
        Interface -> LEDInterface
        {LEDInterface, Backend} -> HardwarePowerBoardBackend
        Component -> LED
        Board -> LEDBoard
   }

The only thing that looks out of place in the above diagram is ``HardwarePowerBoardBackend``, which inherits from both
``LEDInterface`` and ``Backend``. Unlike some other object oriented programming languages, such as Java, Python
has support for a class to inherit from multiple other classes. You can read more here_.

Initially this may seem a bit unintuitive, but we are making use of multiple inheritance in order to create an
interface for each component. As interfaces don't otherwise exist in Python, we have had to re-create them for `j5`.

.. _here: https://www.python-course.eu/python3_multiple_inheritance.php

Structure with Meta-classes
---------------------------

Metaclasses_ are one of the more useful and advanced features of Python and they are instrumental to some of the more
clever features that `j5` has. The below class diagram has metaclasses added.


.. graphviz::

   digraph {
        Interface -> LEDInterface
        {LEDInterface, Backend} -> HardwarePowerBoardBackend
        Component -> LED
        Board -> LEDBoard

        ABCMeta -> BackendMeta
        BackendMeta -> Backend [style=dashed]
        ABCMeta -> {Board, Component, Interface} [style=dashed]
   }

You can view more details about `BackendMeta` in its documentation. `ABCMeta` is part of the Python ``abc`` library.

.. _metaclasses: https://realpython.com/python-metaclasses/

Structure with Attributes
-------------------------

The below diagram shows a class having instances of another class as an attribute with a dotted line.

.. graphviz::

   digraph {
        Interface -> LEDInterface
        {LEDInterface, Backend} -> HardwarePowerBoardBackend
        Component -> LED
        Board -> PowerBoard

        HardwarePowerBoardBackend -> {PowerBoard} [style=dotted]
        PowerBoard -> LED [style=dotted]
        Board -> PowerBoard [style=dotted]
        BoardGroup -> PowerBoard [style=dotted]
        LED -> LEDInterface [style=dotted]
        Robot -> {BoardGroup, PowerBoard}  [style=dotted]
   }

Here we can see how the control flow of the robot is not immediately obvious, but also how we can easily swap out the
modular components within the class structure to support different hardware.

Complete Structure
------------------

This diagram may occasionally be useful, and contains the entire class structure for a single board and component.

.. graphviz::

   digraph {
        Interface -> LEDInterface
        {LEDInterface, Backend} -> HardwarePowerBoardBackend
        Component -> LED
        Board -> PowerBoard

        ABCMeta -> BackendMeta
        BackendMeta -> Backend [style=dashed]

        HardwarePowerBoardBackend -> {PowerBoard} [style=dotted]
        PowerBoard -> LED [style=dotted]
        Board -> PowerBoard [style=dotted]
        BoardGroup -> PowerBoard [style=dotted]
        LED -> LEDInterface [style=dotted]
        Robot -> {BoardGroup, PowerBoard}  [style=dotted]
   }