"""Hardware implementation of the Zoloto Virtual Camera Board."""

from pathlib import Path
from threading import Lock
from typing import Optional, Set, Type

from zoloto import __version__ as zoloto_version
from zoloto.cameras.camera import Camera
from zoloto.marker_dict import MarkerDict

from j5.backends import Backend
from j5.boards import Board
from j5.boards.zoloto import ZolotoCameraBoard
from j5.components import MarkerCameraInterface
from j5.vision import Coordinate, Marker, MarkerList, Orientation


class DefaultCamera(Camera):
    """
    A default camera that doesn't do much.

    Mostly here to ensure sound types.
    """

    marker_dict = MarkerDict.DICT_APRILTAG_36H11

    def get_marker_size(self, marker_id: int) -> int:
        """Get the size of a particular marker."""
        return 10


class ZolotoCameraBoardHardwareBackend(
    MarkerCameraInterface,
    Backend,
):
    """Hardware Backend for Zoloto Camera."""

    board = ZolotoCameraBoard

    @classmethod
    def discover(cls, camera_class: Type[Camera] = DefaultCamera) -> Set[Board]:
        """Discover boards that this backend can control."""
        cameras = camera_class.discover()

        return {
            ZolotoCameraBoard(f"CAM{camera.camera_id}", cls(camera))
            for camera in cameras
        }

    def __init__(self, camera: Camera) -> None:
        self._lock = Lock()

        with self._lock:
            self._zcamera = camera

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version reported by the board."""
        return zoloto_version

    def get_visible_markers(self, identifier: int) -> MarkerList:
        """Get markers that are visible to the camera."""
        markers = MarkerList()

        with self._lock:
            marker_gen = self._zcamera.process_frame_eager()

        for zmarker in marker_gen:
            position = Coordinate(
                # Convert to metres
                zmarker.cartesian.x / 100,
                zmarker.cartesian.y / 100,
                zmarker.cartesian.z / 100,
            )
            orientation = Orientation(zmarker.orientation.quaternion)
            pixel_corners = list(
                map(lambda x: (x.x, x.y), zmarker.pixel_corners),
            )
            pixel_centre = (zmarker.pixel_centre.x, zmarker.pixel_centre.y)

            markers.append(
                Marker(
                    zmarker.id,
                    position,
                    pixel_centre=pixel_centre,
                    pixel_corners=pixel_corners,
                    orientation=orientation,
                ),
            )

        return markers

    def save_annotated_image(self, file: Path) -> None:
        """Save an annotated image to file."""
        with self._lock:
            self._zcamera.save_frame(file, annotate=True)
