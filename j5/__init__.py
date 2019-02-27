"""j5 Robotics API."""

from packaging.version import Version

from .boards import BoardGroup
from .base_robot import BaseRobot

__all__ = ["BoardGroup", "BaseRobot", "__version__"]

__version__ = str(Version("0.0.2"))
