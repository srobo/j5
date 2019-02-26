"""Tests for the Piezo Classes."""

from datetime import timedelta
from typing import List, Optional, Type

import pytest

from j5.backends import Backend
from j5.boards import Board
from j5.components.piezo import Note, Piezo, PiezoInterface, Pitch


class MockPiezoDriver(PiezoInterface):
    """A testing driver for the piezo."""

    def buzz(self, board: Board, identifier: int,
             duration: timedelta, pitch: Pitch) -> None:
        """Queue a pitch to be played."""
        pass


class MockPiezoBoard(Board):
    """A testing board for the piezo."""

    @property
    def name(self) -> str:
        """The name of this board."""
        return "Mock Piezo Board"

    @property
    def serial(self) -> str:
        """The serial number of this board."""
        return "SERIAL"

    @property
    def firmware_version(self) -> Optional[str]:
        """Get the firmware version of this board."""
        return self._backend.get_firmware_version(self)

    @property
    def supported_components(self) -> List[Type['Component']]:
        """List the components that this Board supports."""
        return [Piezo]

    def make_safe(self):
        """Make this board safe."""
        pass

    @staticmethod
    def discover(backend: Backend):
        """Detect all of the boards on a given backend."""
        return []


def test_piezo_interface_implementation():
    """Test that we can implement the PiezoInterface."""
    MockPiezoDriver()


def test_piezo_instantiation():
    """Test that we can instantiate an piezo."""
    Piezo(0, MockPiezoBoard(), MockPiezoDriver())


def test_piezo_interface_class_method():
    """Tests piezo's interface_class method."""
    piezo = Piezo(0, MockPiezoBoard(), MockPiezoDriver())
    assert piezo.interface_class() is PiezoInterface


def test_piezo_buzz_method():
    """Tests piezo's buzz method's input validation."""
    piezo = Piezo(0, MockPiezoBoard(), MockPiezoDriver())
    piezo.buzz(MockPiezoBoard, 0, 0, 2093)
    piezo.buzz(MockPiezoBoard, 0, 0, Note.D7)


def test_piezo_buzz_invalid_value():
    """Test piezo's buzz method's input validation."""
    piezo = Piezo(0, MockPiezoBoard(), MockPiezoDriver())
    with pytest.raises(ValueError):
        piezo.buzz(MockPiezoBoard, 0, 0, -42)
    with pytest.raises(TypeError):
        piezo.buzz(MockPiezoBoard, 0, 0, "j5")
