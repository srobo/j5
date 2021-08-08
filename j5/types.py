"""Useful datatypes that aren't available in the standard lib."""
from typing import Generator, Generic, Iterator, List, Mapping, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")


class ImmutableDict(Generic[T, U]):
    """A dictionary whose elements cannot be set."""

    def __init__(self, members: Mapping[T, U]):
        self._members = members

    def __repr__(self) -> str:
        return f"ImmutableDict({self._members!r})"

    def __getitem__(self, index: T) -> U:
        """
        Get an member using list notation.

        :param index: The key in the dict to fetch.
        :returns: The value of the key in the dict.
        """
        return self._members[index]

    def __iter__(self) -> Iterator[U]:
        """
        Iterate over the members of the dict.

        :returns: Iterator over the members of the dict.
        """
        return iter(self._members.values())

    def __len__(self) -> int:
        """
        Get the number of members in the dict.

        :returns: Number of members in the dict.
        """
        return len(self._members)


class ImmutableList(Generic[T]):
    """A list whose items cannot be set."""

    def __init__(self, members: Union[List[T], Generator[T, None, None]]):
        self._members: List[T] = list(members)

    def __repr__(self) -> str:
        return f"ImmutableList({self._members!r})"

    def __getitem__(self, index: int) -> T:
        """
        Get an member using list notation.

        :param index: The index of the value to fetch.
        :returns: The value at the index.
        """
        return self._members[index]

    def __iter__(self) -> Iterator[T]:
        """
        Iterate over the members of the list.

        :returns: Iterator over the members of the list.
        """
        return iter(self._members)

    def __len__(self) -> int:
        """
        Get the number of members in the list.

        :returns: Number of members in the list.
        """
        return len(self._members)
