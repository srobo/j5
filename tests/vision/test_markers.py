"""Test classes that represent Markers."""

from random import randint, random

from j5.vision.coordinates import Coordinate
from j5.vision.markers import Marker, MarkerList


def get_random_float() -> float:
    """Get a random float between -8 and 8."""
    return (random() - 0.5) * randint(0, 2 * 8)


def get_random_marker() -> Marker:
    """Get a random marker for testing."""
    marker_id = randint(0, 128)
    return Marker(
        marker_id,
        Coordinate(get_random_float(), get_random_float(), get_random_float()),
    )


def test_markers_instantiates() -> None:
    """Test that the marker class can be instantiated."""
    Marker(1, Coordinate(1., 2., 3.))


def test_markers_positions() -> None:
    """Test the properties of the marker class."""
    given_id = 13
    given_position = Coordinate(4., 5., 6.)

    marker = Marker(
        given_id,
        given_position,
    )

    assert(given_id == marker.id)
    assert(given_position == marker.position)


def test_marker_list_instantiation() -> None:
    """Test that we can instantiate a MarkerList."""
    li = [get_random_marker() for _ in range(1, randint(2, 12))]

    marker_list = MarkerList(li)
    assert isinstance(marker_list, MarkerList)
    iter(marker_list)  # Test it's iterable

    marker = marker_list[0]
    assert isinstance(marker, Marker)
