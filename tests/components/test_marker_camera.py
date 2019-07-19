"""Tests for the Marker Camera Component."""

from j5.components.marker_camera import MarkerCamera, MarkerCameraInterface
from j5.vision import Coordinate, Marker, MarkerList


class MockMarkerCameraDriver(MarkerCameraInterface):
    """A testing driver for the Marker Camera."""

    def get_visible_markers(self, identifier: int) -> MarkerList:
        """Get some markers."""
        return MarkerList(
            [Marker(i, Coordinate(0, 0, 0)) for i in range(1, 12)],
        )


def test_marker_camera_interface_implementation() -> None:
    """Test that we can implement the Marker Camera interface."""
    MockMarkerCameraDriver()


def test_marker_camera_instantiation() -> None:
    """Test that we can instantiate a marker camera."""
    MarkerCamera(0, MockMarkerCameraDriver())


def test_marker_camera_interface() -> None:
    """Test that the correct interface class is returned."""
    assert MarkerCamera.interface_class() == MarkerCameraInterface


def test_marker_camera_identifier() -> None:
    """Test that the Marker Camera returns an identifier."""
    m = MarkerCamera(0, MockMarkerCameraDriver())

    assert m.identifier == 0


def test_marker_camera_see() -> None:
    """Test that see returns some markers."""
    m = MarkerCamera(0, MockMarkerCameraDriver())

    reslist = m.see()
    assert isinstance(reslist, MarkerList)
    assert len(reslist) > 0

    m1 = reslist[0]
    assert isinstance(m1, Marker)
