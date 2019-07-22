"""Virtual Camera Board for detecting Fiducial Markers."""

from typing import Optional, Set, Type, cast

from j5.backends import Backend
from j5.boards import Board
from j5.components import Component, MarkerCamera, MarkerCameraInterface


class ZolotoCameraBoard(Board):
    """Virtual Camera Board for detecting fiducial markers."""

    name: str = "Zoloto Camera Board"

    def __init__(self, serial: str, backend: Backend):
        self._serial = serial
        self._backend = backend

        self._camera = MarkerCamera(0, cast(MarkerCameraInterface, backend))

    @property
    def serial(self) -> str:
        """Get the serial number."""
        return self._serial

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of the board."""
        return self._backend.firmware_version

    @property
    def camera(self) -> MarkerCamera:
        """The camera on this board."""
        return self._camera

    def make_safe(self) -> None:
        """Make this board safe."""
        pass

    @staticmethod
    def supported_components() -> Set[Type[Component]]:
        """List the types of components supported by this board."""
        return {
            MarkerCamera,
        }
