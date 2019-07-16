"""Test classes that represent Markers."""

from j5.vision.coordinates import Coordinate
from j5.vision.markers import Marker


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
