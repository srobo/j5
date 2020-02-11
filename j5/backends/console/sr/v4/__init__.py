"""Backends for Student Robotics version 4 boards in the console environment."""

from .motor_board import SRV4MotorBoardConsoleBackend
from .power_board import SRV4PowerBoardConsoleBackend
from .servo_board import SRV4ServoBoardConsoleBackend

__all__ = [
    "SRV4MotorBoardConsoleBackend",
    "SRV4PowerBoardConsoleBackend",
    "SRV4ServoBoardConsoleBackend",
]
