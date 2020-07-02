"""Useful datatypes that aren't available in the standard lib."""
from typing import Generator, Generic, Iterator, List, Mapping, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")


class ImmutableDict(Generic[T, U]):
    """A dictionary whose elements cannot be set."""

    def __init__(self, members: Mapping[T, U]):
        self._members = members

    def __getitem__(self, index: T) -> U:
        """Get an member using list notation."""
        return self._members[index]

    def __iter__(self) -> Iterator[U]:
        """Iterate over the members of the group."""
        return iter(self._members.values())

    def __len__(self) -> int:
        """Get the number of members in the group."""
        return len(self._members)


class ImmutableList(Generic[T]):
    """A list whose items cannot be set."""

    def __init__(self, members: Union[List[T], Generator[T, None, None]]):
        self._members: List[T] = list(members)

    def __getitem__(self, index: int) -> T:
        """Get an member using list notation."""
        return self._members[index]

    def __iter__(self) -> Iterator[T]:
        """Iterate over the members of the group."""
        return iter(self._members)

    def __len__(self) -> int:
        """Get the number of members in the group."""
        return len(self._members)
