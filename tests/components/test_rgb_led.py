"""Tests for the RGB LED component."""
import unittest

from j5.components.rgb_led import RGBLED, RGBColour, RGBLEDInterface


class MockRGBLEDDriver(RGBLEDInterface):
    """A testing driver for the RGB LED."""

    def __init__(self) -> None:
        self._duty_cycles = {colour: 0.5 for colour in RGBColour}  # Initialise

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
        return self._duty_cycles[channel]

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
        self._duty_cycles[channel] = duty_cycle


class TestRGBLEDComponentInterface(unittest.TestCase):
    """Test that the RGB LED Component and Interface behave as expected."""

    def setUp(self) -> None:
        """Set up the test."""
        self._component = RGBLED(0, MockRGBLEDDriver())

    def test_rgb_led_interface_class(self) -> None:
        """Test that the interface class is PWMLEDInterface."""
        assert RGBLED.interface_class() is RGBLEDInterface

    def test_rgb_led_identifier(self) -> None:
        """Test the identifier attribute of the component."""
        self.assertEqual(self._component.identifier, 0)

    def test_rgb_led_get_channel_string(self) -> None:
        """Test getting the duty cycle of a channel by string."""
        self.assertEqual(self._component.get_channel("red"), 0.5)  # Initially set to 0.5

        # Change the state manually
        self._component._backend._duty_cycles[RGBColour.RED] = 0.1  # type: ignore
        self.assertEqual(self._component.get_channel("red"), 0.1)

    def test_rgb_led_get_channel_enum(self) -> None:
        """Test getting the duty cycle of a channel by enum."""
        self.assertEqual(self._component.get_channel(RGBColour.RED), 0.5)

        # Change the state manually
        self._component._backend._duty_cycles[RGBColour.RED] = 0.1  # type: ignore
        self.assertEqual(self._component.get_channel(RGBColour.RED), 0.1)

    def test_rgb_led_get_channel_available_enum(self) -> None:
        """Test that we can get a channel for each of the enum."""
        self.assertEqual(self._component.get_channel(RGBColour.RED), 0.5)
        self.assertEqual(self._component.get_channel(RGBColour.GREEN), 0.5)
        self.assertEqual(self._component.get_channel(RGBColour.BLUE), 0.5)

    def test_rgb_led_get_channel_available_string(self) -> None:
        """Test that we can get a channel for each of the string."""
        self.assertEqual(self._component.get_channel("red"), 0.5)
        self.assertEqual(self._component.get_channel("green"), 0.5)
        self.assertEqual(self._component.get_channel("blue"), 0.5)

        # Also check uppercase
        self.assertEqual(self._component.get_channel("RED"), 0.5)
        self.assertEqual(self._component.get_channel("GREEN"), 0.5)
        self.assertEqual(self._component.get_channel("BLUE"), 0.5)

    def test_rgb_led_get_channel_bad_string(self) -> None:
        """Test that we get an error for a bad channel string."""
        with self.assertRaisesRegex(ValueError, "bees is not a RGB colour"):
            self._component.get_channel("bees")

    def test_rgb_led_set_channel_string(self) -> None:
        """Test setting the duty cycle of a channel by string."""
        self._component.set_channel("red", 0.9)
        self.assertEqual(
            self._component._backend._duty_cycles[RGBColour.RED],  # type: ignore
            0.9,
        )

    def test_rgb_led_set_channel_enum(self) -> None:
        """Test setting the duty cycle of a channel by enum."""
        self._component.set_channel(RGBColour.RED, 0.9)
        self.assertEqual(
            self._component._backend._duty_cycles[RGBColour.RED],  # type: ignore
            0.9,
        )

    def test_rgb_led_set_channel_available_enum(self) -> None:
        """Test that we can set a channel for each of the enum."""
        self._component.set_channel(RGBColour.RED, 0.5)
        self._component.set_channel(RGBColour.GREEN, 0.5)
        self._component.set_channel(RGBColour.BLUE, 0.5)

    def test_rgb_led_set_channel_available_string(self) -> None:
        """Test that we can set a channel for each of the string."""
        self._component.set_channel("red", 0.5)
        self._component.set_channel("green", 0.5)
        self._component.set_channel("blue", 0.5)

        # Also check uppercase
        self._component.set_channel("RED", 0.5)
        self._component.set_channel("GREEN", 0.5)
        self._component.set_channel("BLUE", 0.5)

    def test_rgb_led_set_channel_bad_string(self) -> None:
        """Test that we get an error for a bad channel string."""
        with self.assertRaisesRegex(ValueError, "bees is not a RGB colour"):
            self._component.set_channel("bees", 0.5)

    def test_rgb_led_set_duty_cycle_upper_bound(self) -> None:
        """Test the upper bound on the duty cycle."""
        self._component.set_channel("red", 1)
        self.assertEqual(
            self._component._backend._duty_cycles[RGBColour.RED],  # type: ignore
            1,
        )

        with self.assertRaisesRegex(
            ValueError,
            "PWM LED duty cycle must be between 0 and 1",
        ):
            self._component.set_channel("red", 1.0001)

    def test_rgb_led_set_duty_cycle_lower_bound(self) -> None:
        """Test the lower bound on the duty cycle."""
        self._component.set_channel("red", 0)
        self.assertEqual(
            self._component._backend._duty_cycles[RGBColour.RED],  # type: ignore
            0,
        )

        with self.assertRaisesRegex(
            ValueError,
            "PWM LED duty cycle must be between 0 and 1",
        ):
            self._component.set_channel("red", -0.0001)

    def test_rgb_led_get_red_channel(self) -> None:
        """Test that we can get the red channel."""
        self.assertEqual(self._component.red, 0.5)

        self._component._backend._duty_cycles[RGBColour.RED] = 0.1  # type: ignore
        self.assertEqual(self._component.red, 0.1)

    def test_rgb_led_set_red_channel(self) -> None:
        """Test that we can set the red channel."""
        self._component.red = 0.8
        self.assertEqual(
            self._component._backend._duty_cycles[RGBColour.RED],  # type: ignore
            0.8,
        )

    def test_rgb_led_get_green_channel(self) -> None:
        """Test that we can get the green channel."""
        self.assertEqual(self._component.green, 0.5)

        self._component._backend._duty_cycles[RGBColour.GREEN] = 0.1  # type: ignore
        self.assertEqual(self._component.green, 0.1)

    def test_rgb_led_set_green_channel(self) -> None:
        """Test that we can set the green channel."""
        self._component.green = 0.8
        self.assertEqual(
            self._component._backend._duty_cycles[RGBColour.GREEN],  # type: ignore
            0.8,
        )

    def test_rgb_led_get_blue_channel(self) -> None:
        """Test that we can get the blue channel."""
        self.assertEqual(self._component.blue, 0.5)

        self._component._backend._duty_cycles[RGBColour.BLUE] = 0.1  # type: ignore
        self.assertEqual(self._component.blue, 0.1)

    def test_rgb_led_set_blue_channel(self) -> None:
        """Test that we can set the blue channel."""
        self._component.blue = 0.8
        self.assertEqual(
            self._component._backend._duty_cycles[RGBColour.BLUE],  # type: ignore
            0.8,
        )

    def test_rgb_led_get_rgb_tuple(self) -> None:
        """Test that we can get the colour as a RGB tuple."""
        self.assertEqual(self._component.rgb, (0.5, 0.5, 0.5))

        self._component.red = 1
        self._component.green = 0.6
        self._component.blue = 0
        self.assertEqual(self._component.rgb, (1, 0.6, 0))

    def test_rgb_led_set_rgb_tuple(self) -> None:
        """Test that we can set the colour as a RGB tuple."""
        self._component.rgb = (1, 0.6, 0)

        self.assertEqual(self._component.red, 1)
        self.assertEqual(self._component.green, 0.6)
        self.assertEqual(self._component.blue, 0)

    def test_rgb_led_set_rgb_tuple_out_of_bound(self) -> None:
        """Test that we catch an out of bound value in RGB tuple."""
        with self.assertRaises(ValueError):
            self._component.rgb = (1, 1.2, 0)
