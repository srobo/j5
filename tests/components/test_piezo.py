"""Tests for the Piezo Classes."""

from datetime import timedelta

import pytest

from j5.components.piezo import Note, Piezo, PiezoInterface


class MockPiezoDriver(PiezoInterface):
    """A testing driver for the piezo."""

    def buzz(self, identifier: int,
             duration: timedelta, frequency: float) -> None:
        """Queue a pitch to be played."""
        pass


def test_piezo_interface_implementation() -> None:
    """Test that we can implement the PiezoInterface."""
    MockPiezoDriver()


def test_piezo_instantiation() -> None:
    """Test that we can instantiate an piezo."""
    Piezo(0, MockPiezoDriver())


def test_piezo_interface_class_method() -> None:
    """Tests piezo's interface_class method."""
    piezo = Piezo(0, MockPiezoDriver())
    assert piezo.interface_class() is PiezoInterface


def test_piezo_identifier() -> None:
    """Test the identifier attribute of the component."""
    component = Piezo(0, MockPiezoDriver())
    assert component.identifier == 0


def test_piezo_buzz_method() -> None:
    """Tests piezo's buzz method's input validation."""
    piezo = Piezo(0, MockPiezoDriver())
    piezo.buzz(timedelta(seconds=1), 2093)
    piezo.buzz(timedelta(seconds=1), 2093.23)
    piezo.buzz(timedelta(minutes=1), Note.D7)


def test_piezo_buzz_invalid_value() -> None:
    """Test piezo's buzz method's input validation."""
    piezo = Piezo(0, MockPiezoDriver())
    with pytest.raises(ValueError):
        piezo.buzz(timedelta(seconds=1), -42)
    with pytest.raises(TypeError):
        piezo.buzz(timedelta(seconds=1), "j5")  # type: ignore
    with pytest.raises(ValueError):
        piezo.buzz(timedelta(seconds=-2), Note.D7)
    with pytest.raises(TypeError):
        piezo.buzz(1, Note.D7)  # type: ignore


def test_note_reversed() -> None:
    """Test Note reversed dunder method."""
    assert list(reversed(list(Note))) == list(reversed(Note))
