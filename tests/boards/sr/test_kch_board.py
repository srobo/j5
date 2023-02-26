"""Tests for the SR v4 Motor Board."""

import pytest

from j5.backends import Backend
from j5.boards import Board
from j5.boards.sr import KCHLED, KCHBoard
from j5.components.rgb_led import RGBLED, RGBColour, RGBLEDInterface


class MockKCHBoardBackend(RGBLEDInterface, Backend):
    """A mock KCH backend implementation."""

    board = KCHBoard

    @classmethod
    def discover(cls) -> set[Board]:
        """Discover the Motor Boards on this backend."""
        return set()

    def __init__(self) -> None:
        self._states: list[tuple[float, float, float]] = [
            (0, 0, 0)
            for _ in range(0, 3)
        ]

    @property
    def firmware_version(self) -> str | None:
        """The firmware version of the board."""
        return None

    def get_rgb_led_channel_duty_cycle(
        self,
        identifier: int,
        channel: RGBColour,
    ) -> float:
        """
        Get the duty cycle of a channel on the LED.

        :param identifier: identifier of the RGB LED.
        :param channel: channel to get the duty cycle for.
        :returns: current duty cycle of the LED.
        """
        raise NotImplementedError  # pragma: no cover

    def set_rgb_led_channel_duty_cycle(
        self,
        identifier: int,
        channel: RGBColour,
        duty_cycle: float,
    ) -> None:
        """
        Set the duty cycle of a channel on the LED.

        :param identifier: identifier of the RGB LED.
        :param channel: channel to set the duty cycle of.
        :param duty_cycle: desired duty cycle of the LED.
        """
        raise NotImplementedError  # pragma: no cover


class TestKCHBoard:
    """Test the KCH Board."""

    @pytest.fixture
    def mock_kch(self) -> KCHBoard:
        """A KCH instance with a mock backend."""
        return KCHBoard("SERIAL0", MockKCHBoardBackend())

    def test_supported_components(self) -> None:
        """Test the supported components on the KCH."""
        assert KCHBoard.supported_components() == {RGBLED}

    def test_discover(self) -> None:
        """Test that we can discover KCH boards."""
        assert MockKCHBoardBackend.discover() == set()

    def test_firmware_version(self, mock_kch: KCHBoard) -> None:
        """Test the firmware version on the KCH."""
        assert mock_kch.firmware_version is None

    def test_name(self, mock_kch: KCHBoard) -> None:
        """Test the name attribute of the KCH."""
        assert mock_kch.name == "Student Robotics KCH v1"

    def test_serial_number(self, mock_kch: KCHBoard) -> None:
        """Test the serial attribute of the KCH."""
        assert mock_kch.serial_number == "SERIAL0"

    def test_leds(self, mock_kch: KCHBoard) -> None:
        """Test the LED attributes of the KCH."""
        assert len(mock_kch.leds) == 4
        assert mock_kch.a is mock_kch.leds[KCHLED.A]
        assert mock_kch.b is mock_kch.leds[KCHLED.B]
        assert mock_kch.c is mock_kch.leds[KCHLED.C]
        assert isinstance(mock_kch.leds[KCHLED.START], RGBLED)
