"""Test the Zoloto Camera System."""

from pathlib import Path
from typing import Set

from zoloto import MarkerDict
from zoloto.cameras import Camera

from j5 import BaseRobot, BoardGroup
from j5.backends.hardware.zoloto import ZolotoCameraBoardHardwareBackend
from j5.boards import Board
from j5.boards.zoloto import ZolotoCameraBoard


class ZolotoCamera(Camera):
    """Zoloto Camera."""

    def __init__(self, id: int):
        super().__init__(
            id,
            marker_dict=MarkerDict.DICT_APRILTAG_36H11,
            calibration_file=Path("calibrations.xml"),
        )

    def get_marker_size(self, marker_id: int) -> int:
        """Get the size of a given marker."""
        return 80


class ZolotoCameraBackend(ZolotoCameraBoardHardwareBackend):
    """Camera Backend to override the settings."""

    @classmethod
    def discover(cls) -> Set[Board]:  # type: ignore
        """Discover boards, overriding the parent classes method."""
        return ZolotoCameraBoardHardwareBackend.discover(ZolotoCamera)


class Robot(BaseRobot):
    """A basic robot with a power board."""

    def __init__(self) -> None:
        self.camera_boards = BoardGroup[ZolotoCameraBoard](
            ZolotoCameraBackend,
        )
        self.camera_board: ZolotoCameraBoard = self.camera_boards.singular()


if __name__ == '__main__':

    print("Testing Zoloto Camera.")

    r = Robot()

    print(f"Serial number: {r.camera_board.serial}")
    print(f"Firmware version: {r.camera_board.firmware_version}")

    while True:
        r.camera_board.camera.save("camera.jpg")
        markers = r.camera_board.camera.see()

        print(f"Found {len(markers)} markers.")

        for m in markers:
            print(m)

        print("\r")
