Student Robotics
================

`Student Robotics`_ challenges teams of 16 to 18 year-olds to design, build and develop autonomous robots to compete in
their annual competition. After announcing the year's game, they give teams six months to engineer their creations.
They mentor teams throughout this time, as well as supply them with a kit which provides a framework they can build
their robot around.

Student Robotics is currently on it's fourth generation of robotics kit, which is mostly based around the `ODROID U3`_
and some custom designed hardware that's based on STM32 microcontrollers. The kit communicates with the ODROID using
USB, which has proven to be a more reliable communication method than their previous kits.

Student Robotics Power Board v4
-------------------------------

+------------------+--------------------------------------------------------------+
| Support Level    | Core                                                         |
+------------------+--------------------------------------------------------------+
| Bus              | USB                                                          |
+------------------+--------------------------------------------------------------+
| Board Class      | ``j5.boards.sr.v4.PowerBoard``                               |
+------------------+--------------------------------------------------------------+
| Console Backend  | ``j5.backends.console.sr.v4.SRV4PowerBoardConsoleBackend``   |
+------------------+--------------------------------------------------------------+
| Hardware Backend | ``j5.backends.hardware.sr.v4.SRV4PowerBoardHardwareBackend`` |
+------------------+--------------------------------------------------------------+

The `Power Board v4`_ is a board used for managing power in a Student Robotics Kit, and is powered by a LiPo battery.

The following components are available:

- ``board.battery_sensor`` - A `sensor <Battery Sensor>`_ to monitor the LiPo
- ``board.outputs`` - A dictionary of `Power Outputs <PowerOutput>`_, indexed by :Class:`j5.boards.sr.v4.PowerOutputPosition`.
- ``board.piezo`` - A `Piezo <piezo>`_ buzzer
- ``board.start_button`` - The start `button <Button>`_

The following components also exist, but are not intended for use by competitors:

- ``board._error_led`` - The red "error" `LED <LED>`_
- ``board._run_led`` - The green "run" `LED <LED>`_

Power Outputs
~~~~~~~~~~~~~

.. autoclass:: j5.boards.sr.v4.PowerOutputPosition
    :members:
    :undoc-members:

Student Robotics Motor Board v4
-------------------------------

+------------------+--------------------------------------------------------------+
| Support Level    | Core                                                         |
+------------------+--------------------------------------------------------------+
| Bus              | USB                                                          |
+------------------+--------------------------------------------------------------+
| Board Class      | ``j5.boards.sr.v4.MotorBoard``                               |
+------------------+--------------------------------------------------------------+
| Console Backend  | ``j5.backends.console.sr.v4.SRV4MotorBoardConsoleBackend``   |
+------------------+--------------------------------------------------------------+
| Hardware Backend | ``j5.backends.hardware.sr.v4.SRV4MotorBoardHardwareBackend`` |
+------------------+--------------------------------------------------------------+

The `Motor Board v4`_ is a board used for controlling up to two motors.

The following components are available:

- ``board.motors`` - A list of `motors <Motor>`_ corresponding to the motor outputs.

Student Robotics Servo Board v4
-------------------------------

+------------------+--------------------------------------------------------------+
| Support Level    | Core                                                         |
+------------------+--------------------------------------------------------------+
| Bus              | USB                                                          |
+------------------+--------------------------------------------------------------+
| Board Class      | ``j5.boards.sr.v4.ServoBoard``                               |
+------------------+--------------------------------------------------------------+
| Console Backend  | ``j5.backends.console.sr.v4.SRV4ServoBoardConsoleBackend``   |
+------------------+--------------------------------------------------------------+
| Hardware Backend | ``j5.backends.hardware.sr.v4.SRV4ServoBoardHardwareBackend`` |
+------------------+--------------------------------------------------------------+

The `Servo Board v4`_ is a board used for controlling up to twelve servo motors.

The following components are available:

- ``board.servos`` - A list of `servos <Servo>`_ corresponding to the servo outputs.

Student Robotics Ruggeduino Firmware
------------------------------------

+------------------+---------------------------------------------------------------+
| Support Level    | Core                                                          |
+------------------+---------------------------------------------------------------+
| Bus              | USB                                                           |
+------------------+---------------------------------------------------------------+
| Board Class      | ``j5.boards.sr.v4.Ruggeduino``                                |
+------------------+---------------------------------------------------------------+
| Console Backend  | ``j5.backends.console.sr.v4.SRV4RuggeduinoConsoleBackend``    |
+------------------+---------------------------------------------------------------+
| Hardware Backend | ``j5.backends.hardware.sr.v4.SRV4SRuggeduinoHardwareBackend`` |
+------------------+---------------------------------------------------------------+

The `Ruggeduino`_ is a robust microcontroller for IO based on the `Arduino Uno <https://en.wikipedia.org/wiki/Arduino_Uno>`_.

Student Robotics provides firmware that allows basic control of the Ruggeduino over serial.

The following components are available:

- ``board.pins`` - 18 x `GPIOPin <GPIOPin>`_
- ``board.led`` - 1 x `LED <LED>`_

.. _Student Robotics: https://studentrobotics.org
.. _ODROID U3: https://en.wikipedia.org/wiki/ODROID
.. _Power Board v4: https://studentrobotics.org/docs/kit/power_board
.. _Motor Board v4: https://studentrobotics.org/docs/kit/motor_board
.. _Servo Board v4: https://studentrobotics.org/docs/kit/servo_board
.. _Ruggeduino: https://studentrobotics.org/docs/kit/ruggeduino
