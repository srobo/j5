"""Markers Class."""

from math import atan2, cos, sin, sqrt
from typing import List, NamedTuple


class Coordinate:
    """A position in space."""

    _cart: 'Cartesian' = None
    _cyl: 'Cylindrical' = None
    _sph: 'Spherical' = None

    def __init__(self, x: float, y: float, z: float):
        self._cart = Cartesian(x, y, z)

    @classmethod
    def from_cartesian(cls, x: float, y: float, z: float):
        """Create a coordinate from a cartesian position."""
        return cls(x, y, z)

    @classmethod
    def from_spherical(cls, r: float, theta: float, phi: float):
        """Create a coordinate from a spherical position."""
        return cls(
            r * sin(phi) * cos(theta),
            r * sin(phi) * sin(theta),
            r * cos(phi),
        )

    @classmethod
    def from_cylindrical(cls, p: float, theta: float, z: float):
        """Create a coordinate from a cylindrical position."""
        return cls(
            p * cos(theta),
            p * sin(theta),
            z,
        )

    @property
    def cartesian(self):
        """Cartesian representation."""
        return self._cart

    @property
    def cylindrical(self):
        """Cylindrical representation."""
        if self._cyl is None:
            self._cyl = Cylindrical(
                p=sqrt(self._cart.x**2 + self._cart.y**2),
                theta=atan2(self._cart.y, self._cart.x),
                z=self._cart.z,
            )
        return self._cyl

    @property
    def spherical(self):
        """Spherical representation."""
        if self._sph is None:
            self._sph = Spherical(
                sqrt(self._cart.x**2 + self._cart.y**2 + self._cart.z**2),
                atan2(self._cart.y, self._cart.x),
                atan2(
                    sqrt(self._cart.x**2 + self._cart.y**2),
                    self._cart.z,
                ),
            )
        return self._sph

    def __repr__(self):
        return f"Coordinate(x={self._cart.x}, y={self._cart.y}, z={self._cart.z})"


class Cartesian(NamedTuple):
    """A Cartesian Coordinate."""

    x: float
    y: float
    z: float


class Cylindrical(NamedTuple):
    """A Cylindrical Coordinate.

    p     := axial distance
    theta := azimuth angle (radians)
    z     := height
    """

    p: float
    theta: float
    z: float


class Spherical(NamedTuple):
    """A Spherical Coordinate.

    r     := radial distance
    theta := azimuth angle (radians)
    phi   := polar angle (radians)
    """

    r: float
    theta: float
    phi: float


class Markers():
    """Markers Class.

    The position is stored in self.__position.
    This is a list of coodinates.
    Example:
        [ Coordinate(x1, y1, z1),
          Coordinate(x2, y2, z2),
          Coordinate(x3, y3, z3),
          Coordinate(x4, y4, z4) ]
    """

    __positions: List[Coordinate]

    def __init__(self, positions=[]):
        self.__positions = positions

    @property
    def positions(self) -> List[Coordinate]:
        """Returns the makers positions."""
        return self.__positions

    def add_markers(self, given_positions: List[Coordinate]) -> None:
        """Add marker(s) by providing their coordinates."""
        self.__positions += given_positions
