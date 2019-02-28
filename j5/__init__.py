"""j5 Robotics API."""

from packaging.version import Version

from .base_robot import BaseRobot
from .boards import BoardGroup

__all__ = ["BoardGroup", "BaseRobot", "__version__"]

__version__ = str(Version("0.0.2"))
