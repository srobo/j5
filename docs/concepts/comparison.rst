Comparison to alternatives
==========================

Similar Libraries
-----------------

`j5` was designed to supersede a number of similar libraries. The table below gives a brief comparison between `j5`, `robot-api` / `robotd` and `sr.robot`.

+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
|   Feature                                 | j5                       | robot-api / robotd                   | sr.robot                   |
+===========================================+==========================+======================================+============================+
| Cross-Platform Support                    | Yes                      | No (Requires Linux + udev + systemd) | No (Requires Linux + udev) |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| Custom  / Game Logic without core changes | N/A                      | No                                   | No                         |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| Developer Documentation                   | Yes                      | No                                   | No                         |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| Explanative error messages                | Yes                      | No (Pipe Error)                      | Mostly                     |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| Advanced Fiducial Marker Support          | Upcoming                 | Partial (sb-vision)                  | Yes (Libkoki)              |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| OSI Licence                               | Yes                      | Yes                                  | No                         |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| PEP8 Compliant                            | Yes                      | Non-strict                           | No                         |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| PyPI                                      | Yes                      | No                                   | No                         |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| Python 3                                  | Yes                      | Yes                                  | No                         |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| Run code without hardware                 | Yes (ConsoleEnvironment) | No                                   | No                         |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| Supports multiple environments / backends | Yes                      | Yes                                  | No                         |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| Supports SourceBots Servo Board           | Partial                  | Yes                                  | No                         |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| Supports SR v4 Kit                        | Yes                      | Partial Support                      | Yes                        |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| Test Coverage                             | > 98%                    | Some                                 | No                         |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| Type Checking                             | Yes                      | Partial                              | No                         |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| User Documentation                        | N / A                    | Yes                                  | Yes                        |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+
| Versioning                                | Yes (SemVer)             | Yes                                  | No                         |
+-------------------------------------------+--------------------------+--------------------------------------+----------------------------+

Robot Operating System (ROS)
----------------------------


    The Robot Operating System (ROS) is a flexible framework for writing robot software. It is a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robot behavior across a wide variety of robotic platforms.

The brief paragraph above makes it sound like ROS is very similar to `j5` and the basic idea behind it is. However, `j5` is more suitable for students due to the following:

- Hardware implementation is Python, easier to understand / debug than C++.
- Standard libraries can be used in student code to add custom hardware in `j5`, i.e from Adafruit.
- Smaller codebase.
- Simpler architecture.
- ROS is a real-time operating system, which presents a different way of programming than most students will have been taught.
- ROS is aimed at research environments, `j5` is aimed specifically for robotics competitions.
- ROS is complex
  - The ROS framework is a multi-server distributed computing environment allowing software applications to communicate across server boundaries and thereby acting as one software system.
  - We do not need distributed computing.
  - The more complicated the system, the harder it is to debug. We want to allow students to debug their code.
- ROS does not expose a common API for various hardware. Instead, the appropriate messages must be published to that hardware, which will be different.
- ROS does not have a security model.
- ROS has no automated system for upgrading firmware, nor for updating itself.
- ROS has no configuration management system.
- The ROS messaging system has a fairly large overhead.
- It is non-trivial to add extra hardware support in ROS, raising the barrier to students using non-provided components.

