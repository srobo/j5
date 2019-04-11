Motor Board v4
==============

.. Attention:: This board is not yet supported by j5, but we intend to do so in the future.

udev Rule
---------

If you are connecting the Motor Board to a Linux computer with udev, the following rule can be added in order to access
the Motor Board interface without root privileges:

.. parsed-literal::
    SUBSYSTEM=="tty", DRIVERS=="ftdi_sio", ATTRS{interface}=="MCV4B", GROUP="plugdev", MODE="0666""

It should be noted that ``plugdev`` can be changed to any Unix group of your preference.