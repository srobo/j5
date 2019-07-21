"""Hardware implementation of the Zoloto Virtual Camera Board."""

from os.path import exists
from pathlib import Path, PosixPath
from platform import system
from typing import Optional, Set

from cv2.aruco import DICT_APRILTAG_36H11
from zoloto.cameras.camera import Camera

from j5.backends import Backend
from j5.backends.hardware import HardwareEnvironment
from j5.boards import Board
from j5.boards.zoloto import ZolotoCameraBoard
from j5.components import MarkerCameraInterface
from j5.vision import Coordinate, Marker, MarkerList

CAMERA_PATH = PosixPath("/dev/video0")
CAMERA_SERIAL = "video0"


class ZCamera(Camera):
    """A zoloto camera."""

    def get_marker_size(self, marker_id: int) -> int:
        """Get the size of the marker."""
        return 10


class ZolotoCameraBoardHardwareBackend(
    MarkerCameraInterface,
    Backend,
):
    """Hardware Backend for Zoloto Camera."""

    environment = HardwareEnvironment
    board = ZolotoCameraBoard

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover boards that this backend can control."""
        if system() != "Linux":
            # We currently only support Zoloto on Linux platforms as there is
            # no easy way to detect the presence of webcams on other platforms.
            return set()
        if not exists(CAMERA_PATH):
            # We currently only support a hardcoded path.
            return set()

        return {
            ZolotoCameraBoard("video0", cls(CAMERA_PATH)),
        }

    def __init__(self, device_path: PosixPath) -> None:
        self._device_path = device_path

        self._zoloto = ZCamera(
            0,
            marker_dict=DICT_APRILTAG_36H11,
            calibration_file=str(
                Path(__file__).resolve().parent.joinpath(
                    "C270.xml",
                ),
            ),
        )

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version reported by the board."""
        return None  # Console, so no firmware

    def get_visible_markers(self, identifier: int) -> MarkerList:
        """Get markers that are visible to the camera."""
        markers = MarkerList()

        marker_gen = self._zoloto.process_frame()

        for zmarker in marker_gen:
            position = Coordinate(
                zmarker.cartesian.x,
                zmarker.cartesian.y,
                zmarker.cartesian.z,
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
                ),
            )

        return markers
