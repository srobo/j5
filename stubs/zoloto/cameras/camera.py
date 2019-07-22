"""Stubs for zoloto.camera.camera."""

from pathlib import Path
from typing import Iterator, Optional

from zoloto.marker import Marker


class Camera:
    """Camera class."""

    def __init__(
        self,
        camera_id: int,
        marker_dict: Optional[int] = None,
        calibration_file: Optional[Path] = None,

    ) -> None: ...

    def process_frame(self) -> Iterator[Marker]: ...

    def save_frame(self, path: Path, annotate: bool = False) -> None: ...
