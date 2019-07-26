"""Console backend for the Zoloto Virtual Board."""
from pathlib import Path
from typing import Optional, Set, Type

from j5.backends import Backend
from j5.backends.console import Console, ConsoleEnvironment
from j5.boards import Board
from j5.boards.zoloto import ZolotoCameraBoard
from j5.components import MarkerCameraInterface
from j5.vision import Coordinate, Marker, MarkerList, Orientation


class ZolotoCameraBoardConsoleBackend(
    MarkerCameraInterface,
    Backend,
):
    """Console Backend for Zoloto Camera."""

    environment = ConsoleEnvironment
    board = ZolotoCameraBoard

    @classmethod
    def discover(cls) -> Set[Board]:
        """Discover boards that this backend can control."""
        raise NotImplementedError("The Console Backend cannot discover boards.")

    def __init__(self, serial: str, console_class: Type[Console] = Console) -> None:
        self._serial = serial

        # Setup console helper
        self._console = console_class(f"{self.board.__name__}({self._serial})")

    @property
    def serial(self) -> str:
        """The serial number reported by the board."""
        return self._serial

    @property
    def firmware_version(self) -> Optional[str]:
        """The firmware version reported by the board."""
        return None  # Console, so no firmware

    def get_visible_markers(self, identifier: int) -> MarkerList:
        """Get markers that are visible to the camera."""
        amount = self._console.read(
            f"How many markers are visible to camera {identifier}?",
            int,
        )

        markers = MarkerList()

        for i in range(0, amount):
            marker_id = self._console.read(
                f"What is the id of marker {i}?",
                int,
            )
            marker_x = self._console.read(
                f"What is the x coordinate of marker {i}?",
                float,
            )
            marker_y = self._console.read(
                f"What is the y coordinate of marker {i}?",
                float,
            )
            marker_z = self._console.read(
                f"What is the z coordinate of marker {i}?",
                float,
            )

            orient = self._console.read(
                f"Do you know the orientation of marker {i}?",
                bool,
            )

            orientation = None

            if orient:
                orient_x = self._console.read(
                    f"What is the x rotation of marker {i}?",
                    float,
                )
                orient_y = self._console.read(
                    f"What is the y rotation of marker {i}?",
                    float,
                )
                orient_z = self._console.read(
                    f"What is the z rotation of marker {i}?",
                    float,
                )
                orientation = Orientation.from_cartesian(
                    orient_x,
                    orient_y,
                    orient_z,
                )

            markers.append(
                Marker(
                    marker_id,
                    Coordinate(marker_x, marker_y, marker_z),
                    orientation=orientation,
                ),
            )

        return markers

    def save_annotated_image(self, file: Path) -> None:
        """Save an annotated image to a file."""
        self._console.info(f"Saved annotated image to {file}")
        self._console.info(
            "Image not actually saved due to backend limitations.",
        )
