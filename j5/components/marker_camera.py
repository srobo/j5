"""Classes for Fiducial Marker Camera."""

from abc import abstractmethod
from pathlib import Path
from typing import Type, Union

from j5.components.component import Component, Interface
from j5.vision import MarkerList


class MarkerCameraInterface(Interface):
    """An interface containing the methods required for a marker camera."""

    @abstractmethod
    def get_visible_markers(self, identifier: int) -> MarkerList:
        """Get markers that the camera can see."""
        raise NotImplementedError  # pragma: nocover

    @abstractmethod
    def save_annotated_image(self, file: Path) -> None:
        """Save an annotated image to a file."""
        raise NotImplementedError  # pragma: nocover


class MarkerCamera(Component):
    """
    Camera that can identify fiducial markers.

    Additionally, it will do pose estimation, along with some calibration
    in order to determine the spatial positon and orientation of the markers
    that it has detected.

    This component can be used with systems such as ArUco, LibKoki, etc.
    """

    def __init__(
            self,
            identifier: int,
            backend: MarkerCameraInterface,
    ) -> None:
        self._backend = backend
        self._identifier = identifier

    @staticmethod
    def interface_class() -> Type[MarkerCameraInterface]:
        """Get the interface class that is required to use this component."""
        return MarkerCameraInterface

    @property
    def identifier(self) -> int:
        """An integer to identify the component on a board."""
        return self._identifier

    def see(self) -> MarkerList:
        """
        Capture an image and identify fiducial markers.

        Returns a list of markers that it found.
        """
        return self._backend.get_visible_markers(self._identifier)

    def save(self, path: Union[Path, str]) -> None:
        """Save an annotated image to a path."""
        if isinstance(path, str):
            path = Path(path)
        self._backend.save_annotated_image(path)
