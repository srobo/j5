# j5

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
class Robot(j5.Robot):

    def __init__(self, *args, **kwargs):
        self.power_board = j5.boards.sr.v4power()
        self.motor_board = j5.boards.sr.v4motor()
        self.servo_board = j5.boards.sb.servo_board()
        self.camera_board = j5.boards.sb.camera_board()
```
The above code is for example purposes only and the API is subject to change at any time before it is declared stable.

## Competitions

We are working with the following robotics competition to support their hardware(1):

- SourceBots
- Student Robotics
- Hills Road RoboCon

If you are interested in adding support for your hardware, please get in touch.

## How do I contribute to j5?

`j5` is being developed by a group of volunteers at the University of Southampton. We welcome contributions and reside in a channel on the SourceBots Slack.


(1): Neither Student Robotics nor Hills Road have officially agreed to use this software for their respective competitions. `j5` does not represent any of the competitions listed.
