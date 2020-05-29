"""Test custom types."""
from j5.types import ImmutableDict


def test_immutable_dict_get_member() -> None:
    """Test that we can get an item from an ImmutableDict."""
    d = ImmutableDict[str, str]({'foo': 'bar'})

    assert d['foo'] == 'bar'


def test_immutable_dict_iterator() -> None:
    """Test that the iterator works."""
    data = {'foo': 'bar', 'bar': 'doo', 'doo': 'foo'}

    d = ImmutableDict(data)

    assert [item for item in d] == [item for item in data.values()]


def test_immutable_dict_length() -> None:
    """Test that the length operation works."""
    data = {'foo': 'bar', 'bar': 'doo', 'doo': 'foo'}

    d = ImmutableDict(data)

    assert len(d) == 3
