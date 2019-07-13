"""Tests for the Markers Class."""

from math import isclose

from j5.vision.markers import Coordinate, Cylindrical, Markers, Spherical


def assert_coordinate_isclose(coord1: Coordinate, coord2: Coordinate):
    """Checks two coordinates a roughly equal."""
    assert isclose(coord1.cartesian.x, coord2.cartesian.x)
    assert isclose(coord1.cartesian.y, coord2.cartesian.y)
    assert isclose(coord1.cartesian.z, coord2.cartesian.z)


def assert_cylindrical_isclose(cyl1: Cylindrical, cyl2: Cylindrical):
    """Checks two cylindricals a roughly equal."""
    assert isclose(cyl1.p, cyl2.p)
    assert isclose(cyl1.theta, cyl2.theta)
    assert isclose(cyl1.z, cyl2.z)


def assert_spherical_isclose(sph1: Spherical, sph2: Spherical):
    """Checks two sphericals a roughly equal."""
    assert isclose(sph1.r, sph2.r)
    assert isclose(sph1.theta, sph2.theta)
    assert isclose(sph1.phi, sph2.phi)


def test_coordinates_instantiates() -> None:
    """Test that the coordinate class can be instantiated."""
    Coordinate(1, 2, 3)


def test_coordinate_from_cylindrical() -> None:
    """Test the from_cylindrical() method of the coordinate class."""
    coordinate_1 = Coordinate(3., 4., 5.)
    coordinate_2 = Coordinate(20., 3., 7.)

    cylindrical_1 = Coordinate.from_cylindrical(5., 0.92729521800161, 5.)
    cylindrical_2 = Coordinate.from_cylindrical(20.223748416157, 0.1488899476095, 7.)

    assert_coordinate_isclose(coordinate_1, cylindrical_1)
    assert_coordinate_isclose(coordinate_2, cylindrical_2)


def test_coordinate_from_spherical() -> None:
    """Test the from_spherical() method of the coordiante class."""
    coordinate_1 = Coordinate(3., 4., 5.)
    coordinate_2 = Coordinate(70., 34., 83.)

    spherical_1 = Coordinate.from_spherical(
        7.0710678118655,
        0.92729521800161,
        0.78539816339745,
    )
    spherical_2 = Coordinate.from_spherical(
        113.77609590771,
        0.45215386228578,
        0.75320133230042,
    )

    assert_coordinate_isclose(coordinate_1, spherical_1)
    assert_coordinate_isclose(coordinate_2, spherical_2)


def test_coordinate_from_cartesian() -> None:
    """Test the from_cartestian() method of the coordinate class."""
    coordinate_1 = Coordinate(3., 4., 5.)
    coordinate_2 = Coordinate(20., 3., 7.)

    cartesian_1 = Coordinate.from_cartesian(3., 4., 5.)
    cartesian_2 = Coordinate.from_cartesian(20., 3., 7.)

    assert_coordinate_isclose(coordinate_1, cartesian_1)
    assert_coordinate_isclose(coordinate_2, cartesian_2)


def test_coordinate_cylindrical() -> None:
    """Test the cylindrical property of the coordinate class."""
    coordinate_1 = Coordinate(3., 4., 5.)
    coordinate_2 = Coordinate(20., 3., 7.)

    cylindrical_1 = Cylindrical(p=5., theta=0.92729521800161, z=5.)
    cylindrical_2 = Cylindrical(p=20.223748416157, theta=0.1488899476095, z=7.)

    assert_cylindrical_isclose(coordinate_1.cylindrical, cylindrical_1)
    assert_cylindrical_isclose(coordinate_2.cylindrical, cylindrical_2)


def test_coordinate_spherical() -> None:
    """Test the spherical property of the coordinate class."""
    coordinate_1 = Coordinate(3., 4., 5.)
    coordinate_2 = Coordinate(70., 34., 83.)

    spherical_1 = Spherical(
        r=7.0710678118655,
        theta=0.92729521800161,
        phi=0.78539816339745,
    )
    spherical_2 = Spherical(
        r=113.77609590771,
        theta=0.45215386228578,
        phi=0.75320133230042,
    )

    assert_spherical_isclose(coordinate_1.spherical, spherical_1)
    assert_spherical_isclose(coordinate_2.spherical, spherical_2)


def test_coordinate_represenation() -> None:
    """Test the representation of the coordinate class."""
    coordinate_1 = Coordinate(3., 4., 5.)

    given_representation = coordinate_1.__repr__()
    expected_representation = "Coordinate(x=3.0, y=4.0, z=5.0)"

    assert(given_representation == expected_representation)


def test_markers_instantiates() -> None:
    """Test that the markers class can be instantiated."""
    Markers()


def test_markers_positions() -> None:
    """Test that we can instantiate the markers class."""
    markers = Markers(positions=[
        Coordinate(1., 2., 3.),
    ])

    markers.add_markers([
        Coordinate(4., 5., 6.),
        Coordinate(7., 8., 9.),
    ])

    given_positions = markers.positions
    expected_positions = [
        Coordinate(1., 2., 3.),
        Coordinate(4., 5., 6.),
        Coordinate(7., 8., 9.),
    ]

    for idx in range(0, 3):
        assert_coordinate_isclose(
            given_positions[idx],
            expected_positions[idx],
        )
