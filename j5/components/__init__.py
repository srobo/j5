"""This module contains components, which are the smallest logical element of hardware."""

# We need to import these first as the other files depend on them.
from .component import Component, Interface  # isort:skip

from .battery_sensor import BatterySensor, BatterySensorInterface
from .button import Button, ButtonInterface
from .component import NotSupportedByHardwareError
from .gpio_pin import GPIOPin, GPIOPinInterface, GPIOPinMode
from .led import LED, LEDInterface
from .piezo import Piezo, PiezoInterface
from .power_output import PowerOutput, PowerOutputGroup, PowerOutputInterface
from .servo import Servo, ServoInterface

__all__ = [
    "BatterySensor",
    "BatterySensorInterface",
    "Button",
    "ButtonInterface",
    "Component",
    "GPIOPin",
    "GPIOPinInterface",
    "GPIOPinMode",
    "Interface",
    "LED",
    "LEDInterface",
    "NotSupportedByHardwareError",
    "Piezo",
    "PiezoInterface",
    "PowerOutput",
    "PowerOutputInterface",
    "PowerOutputGroup",
    "Servo",
    "ServoInterface",
]
