"""Markers Class."""

from typing import NamedTuple

import numpy as np


class CylCoords(NamedTuple):
    """Cylindrical Coordinate System.

    p   := axial distance
    phi := azimuth angle (radians)
    z   := height
    """

    p: np.array
    phi: np.array
    z: np.array


class SphCoords(NamedTuple):
    """Spherical Coordinate System.

    r     := radial distance
    theta := polar angle (radians)
    phi   := azimuth angle (radians)
    """

    r: np.array
    theta: np.array
    phi: np.array


class CartCoords(NamedTuple):
    """Cartesian Coordinate System."""

    x: np.array
    y: np.array
    z: np.array


class Markers():
    """Object Class."""

    @staticmethod
    def cart_to_cyl_coords(cart: CartCoords) -> CylCoords:
        """Converts Cartesian Coordinates to Cylindrical Coordinates."""
        cyl = CylCoords(np.sqrt(cart.x**2 + cart.y**2),
                        np.arctan2(cart.y, cart.x),
                        cart.z)
        return cyl

    @staticmethod
    def sph_to_cyl_coords(sph: SphCoords) -> CylCoords:
        """Converts Spherical Coordinates to Cylindrical Coordinates."""
        cyl = CylCoords(sph.r * np.sin(sph.theta),
                        sph.phi,
                        sph.r * np.cos(sph.theta))
        return cyl

    @staticmethod
    def cyl_to_cart_coords(cly: CylCoords) -> CartCoords:
        """Converts Cylindrical Coordinates to Cartesian Coordinates."""
        cart = CartCoords(cly.p * np.cos(cly.phi),
                          cly.p * np.sin(cly.phi),
                          cly.z)
        return cart

    @staticmethod
    def cyl_to_sph_coords(cyl: CylCoords) -> SphCoords:
        """Converts Cylindrical Coordinates to Spherical Coordinates."""
        sph = SphCoords(np.sqrt(cyl.p**2 + cyl.z**2),
                        np.arctan2(cyl.p, cyl.z),
                        cyl.phi)
        return sph
