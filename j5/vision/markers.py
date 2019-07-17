"""Marker Class."""

from typing import List, NewType, Optional, Sequence, Tuple, TypeVar, overload

from .coordinates import Coordinate

Pixel = NewType('Pixel', float)
PixelCoordinates = NewType('PixelCoordinates', Tuple[Pixel, Pixel])


class Marker:
    """
    A fiducial marker.

    Specifically, this class represents a specific measurement of a marker,
    and its position, ID, and in the future, orientation in 3D space.
    """

    _id: int
    _pixel_corners: Optional[Sequence[PixelCoordinates]]
    _position: Coordinate

    def __init__(self,
                 id: int,
                 position: Coordinate,
                 pixel_corners: Optional[Sequence[PixelCoordinates]] = None,
                 ):
        self._id = id
        self._position = position
        self._pixel_corners = pixel_corners

    @property
    def id(self) -> int:
        """The id of the marker."""
        return self._id

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


T = TypeVar("T", bound=Marker)


class MarkerList(List[T]):
    """
    A ``list`` class with nicer error messages.

    In particular, this class provides a slightly better error description when
    accessing indexes and the list is empty.
    This is to mitigate a common beginners issue where a list is indexed
    without checking that the list has any items.
    """

    @overload
    def __getitem__(self, index: int) -> T:
        ...

    @overload  # noqa: F811 (deliberate method replacement)
    def __getitem__(self, index: slice) -> List[T]:
        ...

    def __getitem__(self, index):  # type:ignore  # noqa: F811
        try:
            return super().__getitem__(index)
        except IndexError:
            if not self:
                raise IndexError("Trying to index an empty list") from None
            else:
                raise
