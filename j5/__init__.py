"""j5 Robotics API."""

from .base_robot import BaseRobot
from .boards import BoardGroup

__all__ = ["BoardGroup", "BaseRobot", "__version__", "__version_short__"]

__version__ = "0.7.0"
__version_short__ = "0.7.0"
