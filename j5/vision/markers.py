"""Markers Class."""

from abc import ABCMeta
from typing import List, NamedTuple, Union

import numpy as np


class Coordinate(metaclass=ABCMeta):
    """A position in space."""

    _cart: 'Cartesian'
    _cyl: 'Cylindrical'
    _sph: 'Spherical'

    def __init__(self, x: float, y: float, z: float):
        self._cart = Cartesian(x, y, z)

    @property
    def cartesian(self):
        """Cartesian representation."""
        return self._cart

    @property
    def cylindrical(self):
        """Cylindrical representation."""
        if self._cyl is None:
            self._cyl = Cylindrical(
                p=np.sqrt(self._cart.x**2 + self._cart.y**2),
                phi=np.arctan2(self._cart.y, self._cart.x),
                z=self._cart.z
            )
        return self._cyl

    @property
    def spherical(self):
        """Spherical representation."""
        if self._sph is None:
            self._sph = Spherical(
                np.sqrt(self._cart.x**2 + self._cart.y**2 + self._cart.z**2),
                np.arctan2(self._cart.y, self._cart.x),
                np.arctan2(
                    np.sqrt(self._cart.x**2 + self._cart.y**2),
                    self._cart.z
                )
            )
        return self._sph


class Cartesian(NamedTuple):
    """A Cartesian Coordinate."""

    x: float
    y: float
    z: float


class Cylindrical(NamedTuple):
    """A Cylindrical Coordinate.

    p   := axial distance
    phi := azimuth angle (radians)
    z   := height
    """

    p: float
    phi: float
    z: float


class Spherical(NamedTuple):
    """A Spherical Coordinate.

    r     := radial distance
    theta := polar angle (radians)
    phi   := azimuth angle (radians)
    """

    r: float
    theta: float
    phi: float


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
