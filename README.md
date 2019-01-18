# j5

[![CircleCI](https://circleci.com/gh/j5api/j5.svg?style=svg)](https://circleci.com/gh/j5api/j5)
[![Test Coverage](https://api.codeclimate.com/v1/badges/54e440aba5a51c9ee133/test_coverage)](https://codeclimate.com/github/j5api/j5/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/54e440aba5a51c9ee133/maintainability)](https://codeclimate.com/github/j5api/j5/maintainability)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat)](http://opensource.org/licenses/MIT)

j5 Robotics API - Currently under development.

## What is j5?

`j5` is a Python 3 library that aims to abstract away robotics hardware and provide a consistent API for robotics. It was created to reduce the replication of effort into developing the separate, yet very similar APIs for several robotics competitions. Combining the API into a single library with support for various hardware gives a consistent feel for students and volunteers. This means more time to work on building robots!

## How do I use j5?

`j5` is designed to never be visible to students. It sits behind the scenes and works magic.

```python
from robot import Robot

r = Robot()
r.motor_boards[0].motors[1] = 0.5
```

The above code is likely to be familiar to any student who has competed in one of the below competitions. However, it is not a trivial problem to make this code portable across the platforms. For example, the motor board for Student Robotics is a separate board to the brain board, but is built into the same board for HR RoboCon.

`j5` lets competition vendors define how the basic parts of the apis are accessed. A robot can thus be constructed from any combination of parts from various organisations.

```python
from j5.boards import BoardGroup
from j5.backends.hw import HardwareBackendGroup

from j5.boards.sr.v4 import PowerBoard, MotorBoard, ServoBoard, Ruggeduino


class Robot:

    def __init__(self):

        self._backend_group = HardwareBackendGroup()
        
        self.power_board = PowerBoard(self._backend_group)
        
        self.motor_boards = BoardGroup(MotorBoard, self._backend_group)
        self.motor_board = self.motor_boards.singular()
        
        self.servo_boards = BoardGroup(ServoBoard, self._backend_group)
        self.servo_board = self.servo_boards.singular()
        
        self.ruggeduino = Ruggeduino(self._backend_group)

```

## Competitions

We are working with developers for the following robotics competition to support their hardware(1):

- SourceBots
- Student Robotics
- Hills Road RoboCon

If you are interested in adding support for your hardware, please get in touch.

## Design

As this library has to support multiple hardwares, with multiple backends and still have a common api for people to use, it has ended up fairly complex under the hood. The below diagram should help:

![](/j5.svg)

## How do I contribute to j5?

`j5` is being developed by a group of volunteers at the University of Southampton. We welcome contributions and reside in a channel on the SourceBots Slack.


(1): Neither Student Robotics nor Hills Road have officially agreed to use this software for their respective competitions. `j5` does not represent any of the competitions listed.
