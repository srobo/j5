"""Test the ultrasound sensor component."""
from datetime import timedelta

import pytest

from j5.components import NotSupportedByComponentError
from j5.components.derived.ultrasound import (
    UltrasoundInterface,
    UltrasoundSensor,
)
from j5.components.gpio_pin import GPIOPin, GPIOPinMode
from tests.components.test_gpio_pin import MockGPIOPinDriver


class MockUltrasoundSensorDriver(UltrasoundInterface):
    """A testing driver for the ultrasound sensor."""

    def get_ultrasound_pulse(
            self,
            pin_trigger: int,
            pin_echo: int,
    ) -> timedelta | None:
        """
        Send a pulse and return the time taken.

        Returns None if timeout occurred.
        """
        return timedelta(milliseconds=20)

    def get_ultrasound_distance(
            self,
            pin_trigger: int,
            pin_echo: int,
    ) -> float | None:
        """
        Send a pulse and return the distance to the object.

        Returns None if a timeout occurred.
        """
        const = 1e-6 * 343.0 * 0.5 * 1e3

        time = self.get_ultrasound_pulse(pin_trigger, pin_echo)

        if time is None:
            return None
        return time.microseconds * const


def test_ultrasound_sensor_interface_instantiation() -> None:
    """Test that we can implement an ultrasound interface."""
    MockUltrasoundSensorDriver()


def test_ultrasound_interface() -> None:
    """Test that the ultrasound sensor uses the right interface."""
    assert UltrasoundSensor.interface_class() is UltrasoundInterface


def test_ultrasound_sensor() -> None:
    """Test that we can instantiate an ultrasound sensor."""
    trigger = GPIOPin(
        0,
        MockGPIOPinDriver(),
        initial_mode=UltrasoundSensor,
        firmware_modes={UltrasoundSensor},
    )
    echo = GPIOPin(
        1,
        MockGPIOPinDriver(),
        initial_mode=UltrasoundSensor,
        firmware_modes={UltrasoundSensor},
    )

    u = UltrasoundSensor(trigger, echo, MockUltrasoundSensorDriver())

    time = u.pulse()

    assert time is not None
    assert type(time) is timedelta
    assert time.microseconds == 20000

    dist = u.distance()
    assert dist is not None
    assert type(dist) is float
    assert round(dist) == 3430


def test_ultrasound_no_distance() -> None:
    """Test that we can't get the distance if it's disabled."""
    trigger = GPIOPin(
        0,
        MockGPIOPinDriver(),
        initial_mode=UltrasoundSensor,
        firmware_modes={UltrasoundSensor},
    )
    echo = GPIOPin(
        1,
        MockGPIOPinDriver(),
        initial_mode=UltrasoundSensor,
        firmware_modes={UltrasoundSensor},
    )

    u = UltrasoundSensor(
        trigger,
        echo,
        MockUltrasoundSensorDriver(),
        distance_mode=False,
    )

    with pytest.raises(RuntimeError):
        u.distance()


def test_ultrasound_no_support() -> None:
    """Test that we throw an error on an unsupported pin."""
    trigger = GPIOPin(
        0,
        MockGPIOPinDriver(),
        initial_mode=GPIOPinMode.DIGITAL_OUTPUT,
    )
    echo = GPIOPin(
        1,
        MockGPIOPinDriver(),
        initial_mode=UltrasoundSensor,
        firmware_modes={UltrasoundSensor},
    )

    with pytest.raises(NotSupportedByComponentError):
        UltrasoundSensor(
            trigger,
            echo,
            MockUltrasoundSensorDriver(),
            distance_mode=False,
        )
