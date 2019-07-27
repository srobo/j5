"""Hardware implementation of the Zoloto Virtual Camera Board."""

from pathlib import Path
from platform import system
from typing import Optional, Set, Type, TypeVar

from zoloto import __version__ as zoloto_version
from zoloto.cameras.camera import Camera

from j5.backends import Backend
from j5.backends.hardware import HardwareEnvironment
from j5.boards import Board
from j5.boards.zoloto import ZolotoCameraBoard
from j5.components import MarkerCameraInterface
from j5.vision import Coordinate, Marker, MarkerList, Orientation

CAMERA_PATH = Path("/dev/video0")
CAMERA_SERIAL = "video0"

T = TypeVar("T", bound=Camera)


class DefaultCamera(Camera):
    """
    A default camera that doesn't do much.

    Mostly here to ensure sound types.
    """

    def get_marker_size(self, marker_id: int) -> int:
        """Get the size of a particular marker."""
        return 10


class ZolotoCameraBoardHardwareBackend(
    MarkerCameraInterface,
    Backend,
):
    """Hardware Backend for Zoloto Camera."""

    environment = HardwareEnvironment
    board = ZolotoCameraBoard

    @classmethod
    def discover(cls, camera_class: Type[Camera] = DefaultCamera) -> Set[Board]:
        """Discover boards that this backend can control."""
        if system() != "Linux":
            # We currently only support Zoloto on Linux platforms as there is
            # no easy way to detect the presence of webcams on other platforms.
            return set()
        if not CAMERA_PATH.exists():
            # We currently only support a hardcoded path.
            return set()

        return {
            ZolotoCameraBoard("video0", cls(CAMERA_PATH, camera_class)),
        }

    def __init__(self, device_path: Path, camera_class: Type[T]) -> None:
        self._device_path = device_path

        self._zcamera = camera_class(0)

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version reported by the board."""
        return zoloto_version

    def get_visible_markers(self, identifier: int) -> MarkerList:
        """Get markers that are visible to the camera."""
        markers = MarkerList()

        marker_gen = self._zcamera.process_frame()

        for zmarker in marker_gen:
            position = Coordinate(
                zmarker.cartesian.x,
                zmarker.cartesian.y,
                zmarker.cartesian.z,
            )
            orientation = Orientation.from_cartesian(
                zmarker.orientation.rot_x,
                zmarker.orientation.rot_y,
                zmarker.orientation.rot_z,
            )
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
        self._zcamera.save_frame(file, annotate=True)
