"""Test custom types."""
import pytest

from j5.types import ImmutableDict, ImmutableList


def test_immutable_dict_get_member() -> None:
    """Test that we can get an item from an ImmutableDict."""
    d = ImmutableDict[str, str]({'foo': 'bar'})

    assert d['foo'] == 'bar'


def test_immutable_dict_iterator() -> None:
    """Test that the iterator works."""
    data = {'foo': 'bar', 'bar': 'doo', 'doo': 'foo'}
    d = ImmutableDict(data)

    assert list(d) == list(data.values())


def test_immutable_dict_length() -> None:
    """Test that the length operation works."""
    data = {'foo': 'bar', 'bar': 'doo', 'doo': 'foo'}
    d = ImmutableDict(data)

    assert len(d) == 3


def test_immutable_dict_cannot_set_member() -> None:
    """Test that the immutable dict is immutable."""
    data = {'foo': 'bar', 'bar': 'doo', 'doo': 'foo'}
    d = ImmutableDict(data)

    with pytest.raises(TypeError):
        d['foo'] = '12'  # type: ignore


def test_immutable_list_construct_from_list() -> None:
    """Test that we can construct an ImmutableList from a list."""
    data = [1, 3, 4, 6, 2]
    li = ImmutableList[int](data)
    assert list(li) == data


def test_immutable_list_construct_from_generator() -> None:
    """Test that we can construct an ImmutableList from a generator."""
    data = [1, 3, 4, 6, 2]
    li = ImmutableList[int](item for item in data)
    assert list(li) == data


def test_immutable_list_get_item() -> None:
    """Test that we can get an item from an ImmutableList."""
    data = [1, 3, 4, 6, 2]
    li = ImmutableList[int](data)

    assert li[0] == 1
    assert li[-1] == 2

    with pytest.raises(IndexError):
        li[7]

    with pytest.raises(TypeError):
        li["foo"]  # type:ignore


def test_immutable_list_length() -> None:
    """Test that we can get the list length."""
    data = [1, 3, 4, 6, 2]
    li = ImmutableList[int](data)

    assert len(li) == 5


def test_immutable_list_cannot_set_item() -> None:
    """Test that the list is not immutable."""
    data = [1, 3, 4, 6, 2]
    li = ImmutableList[int](data)

    with pytest.raises(TypeError):
        li[0] = 12  # type: ignore
