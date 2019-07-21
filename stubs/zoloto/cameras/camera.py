"""Stubs for zoloto.camera.camera."""

from pathlib import Path
from typing import Iterator

from zoloto.marker import Marker

class Camera:
    """Camera class."""

    def __init__(
        self,
        camera_id: int,
        *,
        marker_dict: int,
        calibration_file: str,

    ) -> None: ...

    def process_frame(self) -> Iterator[Marker]: ...
