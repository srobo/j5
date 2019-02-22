"""j5 Robotics API."""

from .boards import BoardGroup
from .base_robot import BaseRobot

VERSION = "0.0.2"
SHORT_VERSION = "0.0.2"

__all__ = ["BoardGroup", "BaseRobot", "SHORT_VERSION", "VERSION"]
