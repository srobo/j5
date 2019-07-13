"""Tests for the Markers Class."""

# import numpy as np

# from j5.vision.markers import Cartesian, Cylindrical, Markers, Spherical

from j5.vision.markers import Markers


def test_markers_instantiation() -> None:
    """Test that we can instantiate the markers class."""
    Markers()


# def test_markers_cartesian_to_cylindrical() -> None:
#     """Test the cartesian_to_cylindrical() method of markers class."""
#     cartesian_1 = Cartesian(3., 4., 5.)
#     cartesian_2 = Cartesian(20., 3., 7.)

#     expected_output_1 = Cylindrical(5., 0.92729521800161, 5.)
#     expected_output_2 = Cylindrical(20.223748416157, 0.1488899476095, 7)

#     actual_output_1 = Markers.cartesian_to_cylindrical(cartesian_1)
#     actual_output_2 = Markers.cartesian_to_cylindrical(cartesian_2)

#     assert np.allclose(expected_output_1, actual_output_1)
#     assert np.allclose(expected_output_2, actual_output_2)


# def test_markers_spherical_to_cylindrical() -> None:
#     """Test the spherical_to_cylindrical() method of markers class."""
#     spherical_1 = Spherical(5, 0.25 * np.pi, 0.50 * np.pi)
#     spherical_2 = Spherical(10, 0.60 * np.pi, 0.01 * np.pi)

#     expected_output_1 = Cylindrical(3.535533906,
#                                     1.570796327,
#                                     3.535533906)

#     expected_output_2 = Cylindrical(9.510565163,
#                                     0.03141592654,
#                                     -3.090169944)

#     actual_output_1 = Markers.spherical_to_cylindrical(spherical_1)
#     actual_output_2 = Markers.spherical_to_cylindrical(spherical_2)

#     assert np.allclose(expected_output_1, actual_output_1)
#     assert np.allclose(expected_output_2, actual_output_2)


# def test_markers_cylindrical_to_cartesian() -> None:
#     """Test the cylindrical_to_cartesian() method of markers class."""
#     cylindrical_1 = Cylindrical(3., 0.43 * np.pi, 2.)
#     cylindrical_2 = Cylindrical(10., 1.62 * np.pi, 4.)

#     expected_output_1 = Cartesian(0.6544297242, 2.927750286, 2.)
#     expected_output_2 = Cartesian(3.681245527, -9.297764859, 4.)

#     actual_output_1 = Markers.cylindrical_to_cartesian(cylindrical_1)
#     actual_output_2 = Markers.cylindrical_to_cartesian(cylindrical_2)

#     assert np.allclose(expected_output_1, actual_output_1)
#     assert np.allclose(expected_output_2, actual_output_2)


# def test_markers_cylindrical_to_spherical() -> None:
#     """Test the cylindrical_to_spherical() method of markers class."""
#     cylindrical_1 = Cylindrical(3., 0.43 * np.pi, 2.)
#     cylindrical_2 = Cylindrical(10., 1.62 * np.pi, 4.)

#     expected_output_1 = Spherical(3.605551275, 0.9827937233, 1.350884841)
#     expected_output_2 = Spherical(10.77032961, 1.19028995, 5.089380099)

#     actual_output_1 = Markers.cylindrical_to_spherical(cylindrical_1)
#     actual_output_2 = Markers.cylindrical_to_spherical(cylindrical_2)

#     assert np.allclose(expected_output_1, actual_output_1)
#     assert np.allclose(expected_output_2, actual_output_2)
