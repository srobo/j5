"""Stubs for zoloto.camera.camera."""

from pathlib import Path
from typing import Any, Generator, Iterator, Optional

from zoloto.marker import Marker


class Camera:
    """Camera class."""

    camera_id: int

    def __init__(
        self,
        camera_id: int,
        calibration_file: Optional[Path] = None,

    ) -> None: ...

    def process_frame(self) -> Iterator[Marker]: ...

    def save_frame(self, path: Path, annotate: bool = False) -> None: ...

    @classmethod
    def discover(cls, **kwargs: Any) -> Generator["Camera", None, None]: ...
