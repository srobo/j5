"""Zoloto Coordinates classes.."""

from typing import NamedTuple

from pyquaternion import Quaternion


class Coordinates(NamedTuple):
    x: float
    y: float


class ThreeDCoordinates(NamedTuple):
    x: float
    y: float
    z: float


class Orientation:

    @property
    def quaternion(self) -> Quaternion: ...
