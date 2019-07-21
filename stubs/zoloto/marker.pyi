"""Marker stub for Zoloto."""

from typing import List

from zoloto.coords import Coordinates, ThreeDCoordinates

class Marker:
    """A Zoloto Marker object."""

    @property
    def id(self) -> int: ...

    @property
    def size(self) -> int: ...

    @property
    def pixel_corners(self) -> List[Coordinates]: ...

    @property
    def pixel_centre(self) -> Coordinates: ...

    @property
    def distance(self) -> float: ...

    @property
    def cartesian(self) -> ThreeDCoordinates: ...
