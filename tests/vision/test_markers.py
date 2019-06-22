"""Tests for the Markers Class."""

import numpy as np

from j5.vision.marker import CartCoords, CylCoords, Markers, SphCoords


def test_markers_instantiation() -> None:
    """Test that we can instantiate the markers class."""
    Markers()


def test_markers_cart_to_cyl_coords() -> None:
    """Test the cart_to_cyl_coords() method of markers class."""
    cartesian = CartCoords(np.array([3, 20]),
                           np.array([4, 3]),
                           np.array([5, 7]))

    expected_output = CylCoords(np.array([5, 20.223748416157]),
                                np.array([0.92729521800161,
                                          0.1488899476095]),
                                np.array([5, 7]))
    actual_output = Markers.cart_to_cyl_coords(cartesian)

    assert np.allclose(expected_output, actual_output)


def test_markers_sph_to_cyl_coords() -> None:
    """Test the sph_to_cyl_coords() method of markers class."""
    spherical = SphCoords(np.array([5, 10]),
                          np.array([0.25 * np.pi, 0.60 * np.pi]),
                          np.array([0.50 * np.pi, 0.01 * np.pi]))

    expected_output = CylCoords(np.array([3.535533906,
                                          9.510565163]),
                                np.array([1.570796327,
                                          0.03141592654]),
                                np.array([3.535533906,
                                          -3.090169944]))
    actual_output = Markers.sph_to_cyl_coords(spherical)

    assert np.allclose(expected_output, actual_output)


def test_markers_cyl_to_cart_coords() -> None:
    """Test the cyl_to_cart_coords() method of markers class."""
    cylindrical = CylCoords(np.array([3, 10]),
                            np.array([0.43 * np.pi, 1.62 * np.pi]),
                            np.array([2, 4]))

    expected_output = CartCoords(np.array([0.6544297242,
                                           3.681245527]),
                                 np.array([2.927750286,
                                           -9.297764859]),
                                 np.array([2, 4]))
    actual_output = Markers.cyl_to_cart_coords(cylindrical)

    assert np.allclose(expected_output, actual_output)


def test_markers_cyl_to_sph_coords() -> None:
    """Test the cyl_to_sph_coords() method of markers class."""
    cylindrical = CylCoords(np.array([3, 10]),
                            np.array([0.43 * np.pi, 1.62 * np.pi]),
                            np.array([2, 4]))

    expected_output = SphCoords(np.array([3.605551275,
                                          10.77032961]),
                                np.array([0.9827937233,
                                          1.19028995]),
                                np.array([1.350884841,
                                          5.089380099]))
    actual_output = Markers.cyl_to_sph_coords(cylindrical)

    assert np.allclose(expected_output, actual_output)
