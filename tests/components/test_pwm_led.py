"""Tests for the PWM LED component."""
import unittest

from j5.components.pwm_led import PWMLED, PWMLEDInterface


class MockPWMLEDDriver(PWMLEDInterface):
    """A testing driver for the PWM LED."""

    def __init__(self) -> None:
        self._duty_cycle = 0.5  # Initial duty cycle of 0.5

    def set_pwm_led_duty_cycle(self, identifier: int, duty_cycle: float) -> None:
        """Set the state of an led."""
        self._duty_cycle = duty_cycle

    def get_pwm_led_duty_cycle(self, identifier: int) -> float:
        """Get the state of an LED."""
        return self._duty_cycle


class TestPWMLEDComponentInterface(unittest.TestCase):
    """Test that the PWM LED Component and Interface behave as expected."""

    def setUp(self) -> None:
        """Set up the test."""
        self._component = PWMLED(0, MockPWMLEDDriver())

    def test_pwm_led_interface_class(self) -> None:
        """Test that the interface class is PWMLEDInterface."""
        assert PWMLED.interface_class() is PWMLEDInterface

    def test_pwm_led_identifier(self) -> None:
        """Test the identifier attribute of the component."""
        self.assertEqual(self._component.identifier, 0)

    def test_pwm_led_set_duty_cycle(self) -> None:
        """Test setting of duty_cycle property of an LED."""
        self._component.duty_cycle = 0.1
        self.assertEqual(self._component._backend._duty_cycle, 0.1)  # type: ignore

        self._component.duty_cycle = 0.9
        self.assertEqual(self._component._backend._duty_cycle, 0.9)  # type: ignore

    def test_pwm_led_get_duty_cycle(self) -> None:
        """Test getting of duty_cycle property of an LED."""
        self.assertEqual(self._component.duty_cycle, 0.5)  # Initially set to 0.5

        # Change the state manually
        self._component._backend._duty_cycle = 0.1  # type: ignore
        self.assertEqual(self._component.duty_cycle, 0.1)

    def test_pwm_led_set_duty_cycle_upper_bound(self) -> None:
        """Test the upper bound on the duty cycle."""
        self._component.duty_cycle = 1
        self.assertEqual(self._component.duty_cycle, 1)

        with self.assertRaisesRegex(
            ValueError,
            "PWM LED duty cycle must be between 0 and 1",
        ):
            self._component.duty_cycle = 1.0001

    def test_pwm_led_set_duty_cycle_lower_bound(self) -> None:
        """Test the lower bound on the duty cycle."""
        self._component.duty_cycle = 0
        self.assertEqual(self._component.duty_cycle, 0)

        with self.assertRaisesRegex(
            ValueError,
            "PWM LED duty cycle must be between 0 and 1",
        ):
            self._component.duty_cycle = -0.0001
