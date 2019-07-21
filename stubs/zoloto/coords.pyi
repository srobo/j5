"""
Coordinates classes:
    
These are actually implemented using the coordinates library
"""

class Coordinates:

    @property
    def x(self) -> float: ...

    @property
    def y(self) -> float: ...

class ThreeDCoordinates(Coordinates):

    @property
    def z(self) -> float: ...
