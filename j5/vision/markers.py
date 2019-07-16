"""Marker Class."""

from typing import List, TypeVar, overload

from .coordinates import Coordinate


class Marker:
    """Marker Class.

    Holds a marker's position and id.
    """

    _position: Coordinate
    _id: int

    def __init__(self, id: int, position: Coordinate):
        self._id = id
        self._position = position

    @property
    def id(self) -> int:
        """Returns the id of the marker."""
        return self._id

    @property
    def position(self) -> Coordinate:
        """Returns the position of the marker."""
        return self._position


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
