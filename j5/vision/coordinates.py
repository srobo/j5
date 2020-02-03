"""Coordinate Classes to represent position in space."""

from math import atan2, cos, isclose, sin, sqrt
from typing import NamedTuple

from cached_property import cached_property


class Coordinate:
    """A position in space."""

    _cart: 'Cartesian'

    def __init__(self, x: float, y: float, z: float) -> None:
        self._cart = Cartesian(x, y, z)

    @classmethod
    def from_cartesian(cls, x: float, y: float, z: float) -> 'Coordinate':
        """Create a coordinate from a cartesian position."""
        return cls(x, y, z)

    @classmethod
    def from_spherical(cls, r: float, theta: float, phi: float) -> 'Coordinate':
        """Create a coordinate from a spherical position."""
        return cls(
            r * sin(phi) * cos(theta),
            r * sin(phi) * sin(theta),
            r * cos(phi),
        )

    @classmethod
    def from_cylindrical(cls, p: float, theta: float, z: float) -> 'Coordinate':
        """Create a coordinate from a cylindrical position."""
        return cls(
            p * cos(theta),
            p * sin(theta),
            z,
        )

    @property
    def cartesian(self) -> 'Cartesian':
        """Cartesian representation."""
        return self._cart

    @cached_property
    def cylindrical(self) -> 'Cylindrical':
        """Cylindrical representation."""
        return Cylindrical(
            p=sqrt(self._cart.x**2 + self._cart.y**2),
            phi=atan2(self._cart.y, self._cart.x),
            z=self._cart.z,
        )

    @cached_property
    def spherical(self) -> 'Spherical':
        """Spherical representation."""
        return Spherical(
            sqrt(self._cart.x**2 + self._cart.y**2 + self._cart.z**2),
            atan2(self._cart.y, self._cart.x),
            atan2(
                sqrt(self._cart.x**2 + self._cart.y**2),
                self._cart.z,
            ),
        )

    def __repr__(self) -> str:
        return f"Coordinate(x={self._cart.x}, y={self._cart.y}, z={self._cart.z})"

    def isclose(self, other: 'Coordinate', tolerance: float = 1e-09) -> bool:
        """
        Determine if close to another Coordinate.

        See math.isclose for more information on the behaviour.
        """
        axes = [
            isclose(self._cart.x, other._cart.x, rel_tol=tolerance),
            isclose(self._cart.y, other._cart.y, rel_tol=tolerance),
            isclose(self._cart.z, other._cart.z, rel_tol=tolerance),
        ]

        return all(axes)


class Cartesian(NamedTuple):
    """
    Position in the Cartesian 3D plane.

    x := Displacement from the origin in the x-axis
    y := Displacement from the origin in the y-axis
    z := Displacement from the origin in the z-axis
    """

    x: float
    y: float
    z: float


class Cylindrical(NamedTuple):
    """
    Position in a cylindrical polar coordinate system.

    p     := axial distance
    phi   := azimuth angle (radians)
    z     := height
    """

    p: float
    phi: float
    z: float


class Spherical(NamedTuple):
    """
    A Spherical Coordinate.

    r     := radial distance
    theta := azimuth angle (radians)
    phi   := polar angle (radians)
    """

    r: float
    theta: float
    phi: float
