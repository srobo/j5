"""Test classes that represent Markers."""

from random import randint, random

import pytest

from j5.vision.coordinates import Coordinate
from j5.vision.markers import Marker, MarkerList


def get_random_float() -> float:
    """Get a random float between -8 and 8."""
    return (random() - 0.5) * randint(0, 2 * 8)


def get_random_coordinate() -> Coordinate:
    """Get a random coordinate."""
    return Coordinate(
        get_random_float(),
        get_random_float(),
        get_random_float(),
    )


def get_random_marker() -> Marker:
    """Get a random marker for testing."""
    marker_id = randint(0, 128)
    return Marker(
        marker_id,
        get_random_coordinate(),
    )


def test_markers_instantiates() -> None:
    """Test that the marker class can be instantiated."""
    Marker(1, Coordinate(1., 2., 3.))


def test_markers_position() -> None:
    """Test the properties of the marker class."""
    given_id = 13
    given_position = Coordinate(4., 5., 6.)

    marker = Marker(
        given_id,
        given_position,
    )

    assert(given_id == marker.id)
    assert(given_position == marker.position)


def test_marker_isclose() -> None:
    """Test the isclose method."""
    c = Coordinate(1, 1, 1)

    assert c.isclose(c)
    assert c.isclose(Coordinate(1.00000000001, 1, 1))
    assert not c.isclose(Coordinate(1.1, 1.1, 1.1))


def test_marker_pixel_corners() -> None:
    """Test that pixel corners can be stored."""
    m = Marker(0, get_random_coordinate())
    assert m.pixel_corners is None

    m = Marker(0, get_random_coordinate(), pixel_corners=[])
    assert m.pixel_corners is not None
    assert len(m.pixel_corners) == 0

    m = Marker(0, get_random_coordinate(), pixel_corners=())
    assert m.pixel_corners is not None
    assert len(m.pixel_corners) == 0

    m = Marker(0, get_random_coordinate(), pixel_corners=((12, 12), (34, 43)))
    assert m.pixel_corners is not None
    assert len(m.pixel_corners) == 2
    assert m.pixel_corners[0] == (12, 12)
    assert m.pixel_corners[1] == (34, 43)


def test_marker_pixel_centre() -> None:
    """Test that we can store the pixel centre."""
    m = Marker(0, get_random_coordinate())
    assert m.pixel_centre is None

    m = Marker(0, get_random_coordinate(), pixel_centre=(10, 10))
    assert m.pixel_centre == (10, 10)


def test_marker_distance() -> None:
    """Test that the distance is the expected value."""
    m = get_random_marker()
    assert m.distance is m.position.cylindrical.p


def test_marker_bearing() -> None:
    """Test that the bearing is the expected value."""
    m = get_random_marker()
    assert m.bearing is m.position.cylindrical.phi


def test_marker_str() -> None:
    """Test that the marker string is as expected."""
    m = Marker(4, Coordinate(5, 0, 7))

    assert str(m) == "<Marker 4: 0° left, 5.00m away>"


def test_marker_list_instantiation() -> None:
    """Test that we can instantiate a MarkerList."""
    li = [get_random_marker() for _ in range(1, randint(2, 12))]

    marker_list = MarkerList(li)
    assert isinstance(marker_list, MarkerList)
    iter(marker_list)  # Test it's iterable

    marker = marker_list[0]
    assert isinstance(marker, Marker)


def test_marker_list_friendly_error() -> None:
    """Test that MarkerList is friendly."""
    marker_list = MarkerList([])

    with pytest.raises(IndexError) as e:
        marker_list[0]

        assert e.value == "Trying to index an empty list"

    # Check that it still does it normally too.

    marker_list = MarkerList([get_random_marker()])

    with pytest.raises(IndexError) as e:
        marker_list[1]

        assert e.value != "Trying to index an empty list"
