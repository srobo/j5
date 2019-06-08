"""Test the ultrasound sensor component."""
from datetime import timedelta
from typing import Optional

import pytest
from tests.components.test_gpio_pin import MockGPIOPinDriver

from j5.components.derived.ultrasound import (
    UltrasoundInterface,
    UltrasoundSensor,
)
from j5.components.gpio_pin import GPIOPin


class MockUltrasoundSensorDriver(UltrasoundInterface):
    """A testing driver for the ultrasound sensor."""

    def get_ultrasound_pulse(self, pin_tx: int, pin_rx: int) -> Optional[timedelta]:
        """
        Send a pulse and return the time taken.

        Returns None if timeout occurred.
        """
        return timedelta(milliseconds=20)

    def get_ultrasound_distance(self, pin_tx: int, pin_rx: int) -> Optional[float]:
        """
        Send a pulse and return the distance to the object.

        Returns none if a timeout occurred.
        """
        const = 1e-6 * 343.0 * 0.5 * 1e3

        time = self.get_ultrasound_pulse(pin_tx, pin_rx)

        if time is None:
            return None
        return time.microseconds * const


def test_ultrasound_sensor_interface_instantiation() -> None:
    """Test that we can implement an ultrasound interface."""
    MockUltrasoundSensorDriver()


def test_ultrasound_sensor() -> None:
    """Test that we can instantiate an ultrasound sensor."""
    tx = GPIOPin(
        0,
        MockGPIOPinDriver(),
        initial_mode=UltrasoundSensor,
        supported_modes={UltrasoundSensor},
    )
    rx = GPIOPin(
        0,
        MockGPIOPinDriver(),
        initial_mode=UltrasoundSensor,
        supported_modes={UltrasoundSensor},
    )

    u = UltrasoundSensor(tx, rx, MockUltrasoundSensorDriver())

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
    tx = GPIOPin(
        0,
        MockGPIOPinDriver(),
        initial_mode=UltrasoundSensor,
        supported_modes={UltrasoundSensor},
    )
    rx = GPIOPin(
        0,
        MockGPIOPinDriver(),
        initial_mode=UltrasoundSensor,
        supported_modes={UltrasoundSensor},
    )

    u = UltrasoundSensor(
        tx,
        rx,
        MockUltrasoundSensorDriver(),
        distance_mode=False,
    )

    with pytest.raises(Exception):
        u.distance()
