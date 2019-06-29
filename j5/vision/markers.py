"""Markers Class."""

from __future__ import annotations

from typing import List, NamedTuple, Union

import numpy as np


class Cartesian(NamedTuple):
    """A Cartesian Coordinate."""

    x: float
    y: float
    z: float

    def as_cartesian(self) -> Cartesian:
        """Provides the coordiante in the form of a cartesian coordinate."""
        return self

    def as_cylindrical(self) -> Cylindrical:
        """Provides the coordiante in the form of a cylindrical coordinate."""
        return Cylindrical(np.sqrt(self.x**2 + self.y**2),
                           np.arctan2(self.y, self.x),
                           self.z)

    def as_spherical(self) -> Spherical:
        """Provides the coordiante in the form of a spherical coordinate."""
        return Spherical(np.sqrt(self.x**2 + self.y**2 + self.z**2),
                         np.arctan2(self.y, self.x),
                         np.arctan2(np.sqrt(self.x**2 + self.y**2), self.z))


class Cylindrical(NamedTuple):
    """A Cylindrical Coordinate.

    p   := axial distance
    phi := azimuth angle (radians)
    z   := height
    """

    p: float
    phi: float
    z: float

    def as_cartesian(self) -> Cartesian:
        """Provides the coordiante in the form of a cartesian coordinate."""
        return Cartesian(self.p * np.cos(self.phi),
                         self.p * np.sin(self.phi),
                         self.z)

    def as_cylindrical(self) -> Cylindrical:
        """Provides the coordiante in the form of a cylindrical coordinate."""
        return self

    def as_spherical(self) -> Spherical:
        """Provides the coordiante in the form of a spherical coordinate."""
        return Spherical(np.sqrt(self.p**2 + self.z**2),
                         np.arctan2(self.p, self.z),
                         self.phi)


class Spherical(NamedTuple):
    """A Spherical Coordinate.

    r     := radial distance
    theta := polar angle (radians)
    phi   := azimuth angle (radians)
    """

    r: float
    theta: float
    phi: float

    def as_cartesian(self) -> Cartesian:
        """Provides the coordiante in the form of a cartesian coordinate."""
        return Cartesian(self.r * np.cos(self.phi) * np.sin(self.theta),
                         self.r * np.sin(self.phi) * np.sin(self.theta),
                         self.r * np.cos(self.theta))

    def as_cylindrical(self) -> Cylindrical:
        """Provides the coordiante in the form of a cylindrical coordinate."""
        return Cylindrical(self.r * np.sin(self.theta),
                           self.phi,
                           self.r * np.cos(self.theta))

    def as_spherical(self) -> Spherical:
        """Provides the coordiante in the form of a spherical coordinate."""
        return self


Coordinate = Union[Cylindrical, Spherical, Cartesian]


class Markers():
    """Markers Class.

    The position is stored in self.__position.
    This is a multi-dementional numpy array.
    The first dimesion is the marker index.
    The second dimension is the axis.
    Example:
        [ [x1, y1, z1],
          [x2, y2, z2],
          [x3, y3, z3],
          [x4, y4, z4] ]
    """

    def __init__(self):
        self.__positions = None

    @property
    def positions(self) -> List[Cartesian]:
        """Returns the makers positions."""
        return [Cartesian(*coordinate) for coordinate in self.__positions]

    def add_markers_cartesian(self, given_positions: List[Cartesian]) -> None:
        """Add marker(s) by providing their cartesian coordinates."""
        given_positions = np.array(given_positions)
        self.__append_positions(given_positions)

    def add_markers(self, given_positions: List[Coordinate]) -> None:
        """Add marker(s) by providing their coordinates."""
        given_positions = np.array([position.to_cartesian()
                                    for position in given_positions
                                    ])
        self.__append_positions(given_positions)

    def __append_positions(self, given_positions):
        """Appends a numpy array of markers to the current array (if one exists)."""
        if self.__positions is not None:
            self.__positions = np.concatenate([self.__positions, given_positions])
        else:
            self.__positions = given_positions

    def translate_space(self, delta_x, delta_y, delta_z):
        """Move translate the markers."""
        self.__positions \
            = self.__positions \
            + np.array([delta_x, delta_y, delta_z])

    def rotate_about_x(self, rot_x):
        """Rotate all the markers about the x axis."""
        x_rotation = np.array([[1, 0, 0],
                               [0, np.cos(rot_x), -np.sin(rot_x)],
                               [0, np.sin(rot_x), np.cos(rot_x)]])
        self.__positions = np.multiply(self.__positions, x_rotation)

    def rotate_about_y(self, rot_y):
        """Rotate all the markers about the y axis."""
        y_rotation = np.array([[np.cos(rot_y), 0, np.sin(rot_y)],
                               [0, 1, 0],
                               [-np.sin(rot_y), 0, np.cos(rot_y)]])
        self.__positions = np.multiply(self.__positions, y_rotation)

    def rotate_about_z(self, rot_z):
        """Rotate all the markers about the z axis."""
        z_rotation = np.array([[np.cos(rot_z), -np.sin(rot_z), 0],
                               [np.sin(rot_z), np.cos(rot_z), 0],
                               [0, 0, 1]])
        self.__positions = np.multiply(self.__positions, z_rotation)

    @staticmethod
    def cartesian_to_cylindrical(cart: Cartesian) -> Cylindrical:
        """Converts a cartesian coordinate to a cylindrical coordinate."""
        return Cylindrical(np.sqrt(cart.x**2 + cart.y**2),
                           np.arctan2(cart.y, cart.x),
                           cart.z)

    @staticmethod
    def cartesian_to_spherical(cart: Cartesian) -> Spherical:
        """Converts a cartesian coordinate to a spherical coordinate."""
        return Spherical(np.sqrt(cart.x**2 + cart.y**2 + cart.z**2),
                         np.arctan2(cart.y, cart.x),
                         np.arctan2(np.sqrt(cart.x**2 + cart.y**2), cart.z))

    @staticmethod
    def cylindrical_to_cartesian(cyl: Cylindrical) -> Cartesian:
        """Converts a cylindrical coordinate to a cartesian coordinate."""
        return Cartesian(cyl.p * np.cos(cyl.phi),
                         cyl.p * np.sin(cyl.phi),
                         cyl.z)

    @staticmethod
    def cylindrical_to_spherical(cyl: Cylindrical) -> Spherical:
        """Converts a cylindrical coordinate to a spherical coordinate."""
        return Spherical(np.sqrt(cyl.p**2 + cyl.z**2),
                         np.arctan2(cyl.p, cyl.z),
                         cyl.phi)

    @staticmethod
    def spherical_to_cylindrical(sph: Spherical) -> Cylindrical:
        """Converts a spherical coordinate to a cylindrical coordinate."""
        return Cylindrical(sph.r * np.sin(sph.theta),
                           sph.phi,
                           sph.r * np.cos(sph.theta))

    @staticmethod
    def spherical_to_cartesian(sph: Spherical) -> Cartesian:
        """Converts a spherical coordinate to a cartesian coordinate."""
        return Cartesian(sph.r * np.cos(sph.phi) * np.sin(sph.theta),
                         sph.r * np.sin(sph.phi) * np.sin(sph.theta),
                         sph.r * np.cos(sph.theta))
