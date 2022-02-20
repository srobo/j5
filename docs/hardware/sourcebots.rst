SourceBots
==========

SourceBots is a not-for-profit organisation aiming to promote Science, Technology, Engineering and Mathematics (STEM) subjects to teenagers. It does this by hosting robotics challenges which encourage participants to work together in an environment markedly different to the way they would at school or college.

SourceBots' kit is largely similar to the `Student Robotics <Student Robotics>`_ kit.

SourceBots Arduino Firmware
---------------------------

+------------------+--------------------------------------------------------------+
| Support Level    | Core                                                         |
+------------------+--------------------------------------------------------------+
| Bus              | USB                                                          |
+------------------+--------------------------------------------------------------+
| Board Class      | ``j5.boards.sb.SBArduinoBoard``                              |
+------------------+--------------------------------------------------------------+
| Console Backend  | ``j5.backends.console.sb.arduino.SBArduinoConsoleBackend``   |
+------------------+--------------------------------------------------------------+
| Hardware Backend | ``j5.backends.hardware.sb.arduino.SBArduinoHardwareBackend`` |
+------------------+--------------------------------------------------------------+

The `SourceBots Arduino firmware <https://github.com/sourcebots/arduino-fw>`_ is designed for use on an `Arduino Uno <https://en.wikipedia.org/wiki/Arduino_Uno>`_.

It can be used to control the GPIO pins of the Arduino and measure distances using HC-SR04 ultrasonic sensors.

The following components are available:

- ``board.pins`` - 18 x `GPIOPin <GPIOPin>`_
- ``board.led`` - 1 x `LED <LED>`_