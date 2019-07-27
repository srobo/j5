"""Marker Class."""

from math import degrees
from typing import List, Optional, Sequence, Tuple, overload

from .coordinates import Coordinate
from .orientation import Orientation

PixelCoordinates = Tuple[float, float]


class Marker:
    """
    A fiducial marker.

    Specifically, this class represents a specific measurement of a marker,
    and its position, ID, and in the future, orientation in 3D space.
    """

    _id: int
    _orientation: Optional[Orientation]
    _pixel_corners: Optional[Sequence[PixelCoordinates]]
    _pixel_centre: Optional[PixelCoordinates]
    _position: Coordinate

    def __init__(self,
                 id: int,
                 position: Coordinate,
                 pixel_corners: Optional[Sequence[PixelCoordinates]] = None,
                 pixel_centre: Optional[PixelCoordinates] = None,
                 *,  # We need to move this before pixel_corners.
                 orientation: Optional[Orientation] = None,
                 ):
        self._id = id
        self._orientation = orientation
        self._position = position
        self._pixel_corners = pixel_corners
        self._pixel_centre = pixel_centre

    @property
    def id(self) -> int:
        """The id of the marker."""
        return self._id

    @property
    def bearing(self) -> float:
        """Bearing to the marker from the origin, in radians."""
        return self.position.cylindrical.phi

    @property
    def distance(self) -> float:
        """Distance to the marker from the origin, in metres."""
        return self.position.cylindrical.p

    @property
    def orientation(self) -> Optional[Orientation]:
        """Orientation of the Marker."""
        return self._orientation

    @property
    def position(self) -> Coordinate:
        """Position of the marker."""
        return self._position

    @property
    def pixel_corners(self) -> Optional[Sequence[PixelCoordinates]]:
        """
        Pixel positions of the marker corners within the image.

        Specified in clockwise order, starting from the top left corner of the
        marker. Pixels are counted from the origin of the image, which
        conventionally is in the top left corner of the image.

        This is made available so that if users want to use their own pose
        estimation algorithms, they can!
        """
        return self._pixel_corners

    @property
    def pixel_centre(self) -> Optional[PixelCoordinates]:
        """
        Pixel positions of the centre of the marker within the image.

        Pixels are counted from the origin of the image, which
        conventionally is in the top left corner of the image.

        This is made available so that if users want to use their own pose
        estimation algorithms, they can!
        """
        return self._pixel_centre

    def __str__(self) -> str:
        return "<Marker {}: {:.0f}° {}, {:.2f}m away>".format(
            self.id,
            abs(degrees(self.bearing)),
            "right" if self.bearing > 0 else "left",
            self.distance,
        )


class MarkerList(List[Marker]):
    """
    A ``list`` class with nicer error messages.

    In particular, this class provides a slightly better error description when
    accessing indexes and the list is empty.
    This is to mitigate a common beginners issue where a list is indexed
    without checking that the list has any items.
    """

    @overload
    def __getitem__(self, index: int) -> Marker:
        ...  # pragma: nocover

    @overload  # noqa: F811 (deliberate method replacement)
    def __getitem__(self, index: slice) -> List[Marker]:
        ...  # pragma: nocover

    def __getitem__(self, index):  # type:ignore  # noqa: F811
        try:
            return super().__getitem__(index)
        except IndexError:
            if not self:
                raise IndexError("Trying to index an empty list") from None
            else:
                raise
