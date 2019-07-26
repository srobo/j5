"""
Coordinates classes:
    
These are actually implemented using the coordinates library
"""

from typing import NamedTuple

class Coordinates:

    @property
    def x(self) -> float: ...

    @property
    def y(self) -> float: ...


class ThreeDCoordinates(Coordinates):

    @property
    def z(self) -> float: ...


class Orientation(NamedTuple):

    @property
    def rot_x(self) -> float: ...

    @property
    def rot_y(self) -> float: ...

    @property
    def rot_z(self) -> float: ...
