Supported Hardware
==================

j5 is primarily a framework around which hardware implementations can be built.

However, there are a number of common devices which have implementations provided by j5.

Support Levels
--------------

These implementation are split into a number of support levels:

- *Core* -  This implementation is part of the core ``j5`` library.
- *Supported* - This implementation is officially supported by j5.
- *3rd Party* - This implementation is not supported by j5.

Available Integrations
----------------------

The following integrations are available: 

+------------------+---------------------------------+---------------+
| Vendor           | Name                            | Support Level |
+==================+=================================+===============+
| SourceBots       | Arduino Uno Firmware            | Core          |
+------------------+---------------------------------+---------------+
| Student Robotics | KCH v1                          | Core          |
+------------------+---------------------------------+---------------+
| Student Robotics | Motor Board v4                  | Core          |
+------------------+---------------------------------+---------------+
| Student Robotics | Power Board v4                  | Core          |
+------------------+---------------------------------+---------------+
| Student Robotics | Ruggeduino Firmware             | Core          |
+------------------+---------------------------------+---------------+
| Student Robotics | Servo Board v4                  | Core          |
+------------------+---------------------------------+---------------+
| Zoloto           | Fiducial Marker Pose Estimation | Supported     |
+------------------+---------------------------------+---------------+

.. _Zoloto: https://j5api.github.io/j5-zoloto/

.. toctree::
    :maxdepth: 1
    :caption: Vendors

    sourcebots
    srobo
    Zoloto <https://j5api.github.io/j5-zoloto/>
